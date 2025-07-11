import asyncio
from playwright.async_api import async_playwright
import os
import json
import platform
import uuid
from datetime import datetime

async def sync_fill_form(url, field_data):
    async with async_playwright() as p:
        try:
            print(f"Launching browser for URL: {url}")
            launch_args = ['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage']
            if platform.system() == "Windows":
                launch_args.append('--disable-features=NetworkService')

            browser = await p.chromium.launch(headless=True, args=launch_args)
            page = await browser.new_page()

            absolute_url = url if url.startswith("http") else f"file://{os.path.abspath(url)}"
            print(f"Navigating to: {absolute_url}")
            await page.goto(absolute_url, wait_until="networkidle", timeout=60000)

            for key, value in field_data.items():
                selector = f"[name='{key}']"
                if await page.query_selector(selector):
                    if isinstance(value, str) and os.path.exists(value):
                        print(f"Uploading file for {key}")
                        await page.set_input_files(selector, value)
                    else:
                        print(f"Filling {key} with {value}")
                        await page.fill(selector, str(value))
                else:
                    print(f"Warning: Field {key} not found.")

            for _ in range(5):
                next_btn = await page.query_selector("button.next, input.next")
                submit_btn = await page.query_selector("button[type='submit'], input[type='submit']")
                if next_btn:
                    print("Clicking Next button")
                    await next_btn.click()
                    await page.wait_for_load_state("networkidle")
                elif submit_btn:
                    print("Clicking Submit button")
                    await submit_btn.click()
                    await page.wait_for_load_state("networkidle")
                    break
                else:
                    print("No Next or Submit button found")
                    break

            # Ensure submission_log.json is saved correctly
            log_path = os.path.join(os.getcwd(), "submission_log.json")
            if not os.path.exists(log_path):
                with open(log_path, "w") as f:
                    json.dump([], f)
            with open(log_path, "r+") as f:
                data = json.load(f)
                entry = {
                    "id": str(uuid.uuid4()),
                    "url": url,
                    "data": dict(field_data),
                    "timestamp": datetime.now().isoformat()
                }
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
            print(f"Form submission data saved to {log_path}")

        except Exception as e:
            print(f"Error during form submission: {str(e)}")
            raise
        finally:
            await browser.close()
            print("Browser closed")