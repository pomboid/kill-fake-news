import asyncio
import json
import os
import sys
from datetime import datetime
from glob import glob

# Add parent directory to path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import select
from core.database import get_session, init_db, engine
from core.sql_models import Article, Analysis, Verification, Source

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

async def migrate_sources():
    print("Migrating sources...")
    sources = [
        {"name": "G1", "url": "https://g1.globo.com", "type": "reference"},
        {"name": "Folha", "url": "https://www.folha.uol.com.br", "type": "reference"},
        {"name": "UOL", "url": "https://www.uol.com.br", "type": "reference"},
        {"name": "BBC Brasil", "url": "https://www.bbc.com/portuguese", "type": "reference"},
        {"name": "CNN Brasil", "url": "https://www.cnnbrasil.com.br", "type": "reference"},
        {"name": "Estadão", "url": "https://www.estadao.com.br", "type": "reference"},
    ]
    
    async for session in get_session():
        for s_data in sources:
            statement = select(Source).where(Source.name == s_data["name"])
            existing = (await session.exec(statement)).first()
            if not existing:
                source = Source(**s_data)
                session.add(source)
                print(f"Added source: {s_data['name']}")
        await session.commit()

async def migrate_articles():
    print("Migrating articles...")
    raw_files = glob(os.path.join(DATA_DIR, "raw", "*.jsonl"))
    
    async for session in get_session():
        for file_path in raw_files:
            print(f"Processing {file_path}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        url = data.get("url")
                        if not url: continue
                        
                        # Check exist
                        statement = select(Article).where(Article.url == url)
                        existing = (await session.exec(statement)).first()
                        if existing: continue
                        
                        # Parse date
                        pub_date = None
                        if data.get("data_publicacao"):
                            try:
                                pub_date = datetime.fromisoformat(data.get("data_publicacao"))
                            except: pass
                            
                        article = Article(
                            title=data.get("titulo", "")[:500],
                            subtitle=data.get("subtitulo"),
                            url=url,
                            content=data.get("corpo_do_texto", ""),
                            author=data.get("autor", "Redação"),
                            published_at=pub_date
                        )
                        session.add(article)
                    except Exception as e:
                        print(f"Error parsing line: {e}")
            await session.commit()

async def migrate_analysis():
    print("Migrating analysis...")
    analysis_files = glob(os.path.join(DATA_DIR, "analysis", "*.jsonl"))
    
    async for session in get_session():
        for file_path in analysis_files:
            print(f"Processing {file_path}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        data = json.loads(line)
                        url = data.get("url") # Assuming analysis JSONL has URL or link to it
                        if not url: continue
                        
                        # Find article
                        statement = select(Article).where(Article.url == url)
                        article = (await session.exec(statement)).first()
                        if not article:
                            print(f"Article not found for analysis: {url}")
                            continue

                        # Check exist
                        statement = select(Analysis).where(Analysis.article_id == article.id)
                        existing = (await session.exec(statement)).first()
                        if existing: continue

                        analysis = Analysis(
                            article_id=article.id,
                            is_fake=data.get("is_fake", False),
                            confidence=data.get("confidence_score", 0.0),
                            reasoning=data.get("reasoning", ""),
                            markers=data.get("detected_markers", []),
                            scores=data.get("scores", {}).dict() if hasattr(data.get("scores"), "dict") else data.get("scores", {})
                        )
                        session.add(analysis)
                    except Exception as e:
                        print(f"Error parsing analysis: {e}")
            await session.commit()

async def list_tables():
     async for session in get_session():
        result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        print("Tables in DB:", [row[0] for row in result])

async def migrate_history():
    print("Migrating verification history...")
    history_file = os.path.join(DATA_DIR, "verification_history.jsonl")
    if not os.path.exists(history_file):
        print("No history file found.")
        return

    async for session in get_session():
        with open(history_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    claim = data.get("claim")
                    if not claim: continue
                    
                    # Check exist (by timestamp and claim)
                    # timestamp might be string
                    ts_str = data.get("timestamp")
                    ts = None
                    if ts_str:
                        try:
                            ts = datetime.fromisoformat(ts_str)
                        except: pass
                    
                    # Rough check to avoid exact dupe
                    statement = select(Verification).where(Verification.claim == claim).where(Verification.created_at == ts)
                    existing = (await session.exec(statement)).first()
                    if existing: continue

                    verification = Verification(
                        user_id=data.get("user_id"),
                        claim=claim[:5000],  # Limit length
                        verdict=data.get("veredito", "INCONCLUSIVO"),
                        confidence=data.get("confianca", 0.0),
                        evidence=data.get("evidencias", []),
                        created_at=ts or datetime.utcnow()
                    )
                    session.add(verification)
                except Exception as e:
                    print(f"Error parsing history: {e}")
        await session.commit()

async def main():
    print("Starting migration...")
    await init_db()
    await migrate_sources()
    await migrate_articles()
    await migrate_analysis()
    await migrate_history()
    print("Migration complete!")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
