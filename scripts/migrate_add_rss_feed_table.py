"""
Migration: Adiciona tabela rss_feed e atualiza schema da tabela source

Este script:
1. Cria a nova tabela rss_feed
2. Atualiza a tabela source (adiciona display_name, website_url)
3. Mantém dados existentes

Uso:
    python scripts/migrate_add_rss_feed_table.py
"""
import asyncio
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import AsyncSession, engine
from core.sql_models import Source, RSSFeed, SQLModel, Article, Analysis, Verification
from sqlmodel import select

async def migrate():
    """Executa migration"""
    print("🔧 Iniciando migration...")

    # Criar todas as tabelas (incluindo rss_feed)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    print("✅ Tabelas criadas/atualizadas com sucesso")

    # Verificar sources existentes e atualizar schema se necessário
    async with AsyncSession(engine) as session:
        result = await session.execute(select(Source))
        sources = result.scalars().all()

        if sources:
            print(f"\n📊 Encontradas {len(sources)} sources existentes:")
            for source in sources:
                print(f"  - {source.name}")

                # Se source ainda não tem display_name, atualizar
                if not hasattr(source, 'display_name') or not source.display_name:
                    source.display_name = source.name
                    print(f"    ✅ Adicionado display_name: {source.display_name}")

                # Se source ainda não tem website_url, usar o url antigo
                if not hasattr(source, 'website_url') or not source.website_url:
                    if hasattr(source, 'url'):
                        source.website_url = source.url
                    else:
                        source.website_url = f"https://{source.name.lower()}.com"
                    print(f"    ✅ Adicionado website_url: {source.website_url}")

            await session.commit()
            print("\n✅ Sources atualizadas")
        else:
            print("\n⚠️  Nenhuma source existente encontrada")
            print("   Execute o seed script para popular o banco de dados")

    print("\n✅ Migration concluída com sucesso!")
    print("\n📝 Próximos passos:")
    print("   1. Execute: python scripts/seed_rss_feeds.py")
    print("   2. Execute: python main.py collect")

if __name__ == "__main__":
    try:
        asyncio.run(migrate())
    except Exception as e:
        print(f"\n❌ Erro durante migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
