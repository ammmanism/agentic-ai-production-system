import asyncio
from playwright.async_api import async_playwright
import os

async def record():
    async with async_playwright() as p:
        # Launch browser (pointing to Brave if you prefer, or default Chromium)
        browser = await p.chromium.launch(headless=False) 
        
        # Create a context with video recording enabled
        context = await browser.new_context(
            record_video_dir="media/temp_video/",
            viewport={"width": 1280, "height": 800}
        )
        
        page = await context.new_page()
        
        # --- SCENE 1: THE README ---
        print("Scrubbing README...")
        await page.goto("https://github.com/ammmanism/agentic-ai-production-system")
        await page.wait_for_timeout(2000)
        
        # Smooth scroll
        for i in range(5):
            await page.mouse.wheel(0, 400)
            await page.wait_for_timeout(1000)
            
        # --- SCENE 2: SOURCE CODE ---
        print("Exploring Source Code...")
        await page.click("text=orchestration")
        await page.wait_for_timeout(2000)
        await page.go_back()
        
        # --- SCENE 3: EXPERIMENTS ---
        print("Checking Researchers Suite...")
        await page.click("text=experiments")
        await page.wait_for_timeout(2000)
        
        await context.close()
        await browser.close()
        
        # Find the video file and rename it
        video_files = os.listdir("media/temp_video/")
        if video_files:
            os.rename(f"media/temp_video/{video_files[0]}", "media/automated_showcase.webm")
            print("🚀 SUCCESS! Video saved to media/automated_showcase.webm")

if __name__ == "__main__":
    if not os.path.exists("media/temp_video/"):
        os.makedirs("media/temp_video/", exist_ok=True)
    asyncio.run(record())
