import asyncio
import json
import os
from mcp_server import scrape_github, analyze_profile, generate_card_html
from dotenv import load_dotenv

load_dotenv()

async def test_end_to_end():
    username = "torvalds"
    print(f"Testing end-to-end for: {username}")
    
    try:
        # 1. Scrape GitHub
        print("Step 1: Scraping GitHub...")
        github_data = await scrape_github(username)
        print("Scrape successful.")
        
        # 2. Analyze Profile
        print("Step 2: Analyzing Profile with Gemini...")
        analysis = await analyze_profile(github_data)
        print("Analysis successful.")
        
        # 3. Generate HTML Card
        print("Step 3: Generating HTML Card...")
        html_card = await generate_card_html(username, github_data, analysis)
        print("HTML Generation successful.")
        
        # 4. Print Results
        print("\n--- Results ---")
        print(f"Card Theme: {analysis.get('card_theme')}")
        print(f"Developer Vibe: {analysis.get('developer_vibe')}")
        
    except Exception as e:
        print(f"\n[!] Tool failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_end_to_end())
