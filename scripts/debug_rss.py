
import asyncio
import httpx
import re

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
}

URL = "https://g1.globo.com/rss/g1/tecnologia/"

async def debug_rss():
    print(f"Fetching {URL}...")
    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        try:
            resp = await client.get(URL)
            print(f"Status: {resp.status_code}")
            
            content = resp.text
            print(f"Content Length: {len(content)}")
            print("-" * 50)
            print(content[:500])
            print("-" * 50)
            
            # Debug Regex
            print("Trying default regex: r'<(item|entry).*?>(.*?)</\\1>'")
            items = re.findall(r'<(item|entry).*?>(.*?)</\1>', content, re.DOTALL)
            print(f"Found {len(items)} items using default regex.")
            
            if items:
                print("First item sample:")
                print(items[0][1][:200])
            else:
                print("Trying fallback regex: r'<item>(.*?)</item>'")
                items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
                print(f"Found {len(items)} items using fallback regex.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_rss())
