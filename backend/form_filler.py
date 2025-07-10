from playwright.sync_api import sync_playwright
import os
import json
import platform

def sync_fill_form(url, field_data):
    with sync_playwright() as p:
        try:
            print(f"Launching browser for URL: {url}")
            launch_args = ['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage']
            if platform.system() == "Windows":
                launch_args.append('--disable-features=NetworkService')

            browser = p.chromium.launch(headless=True, args=launch_args)
            page = browser.new_page()

            absolute_url = url if url.startswith("http") else f"file://{os.path.abspath(url)}"
            print(f"Navigating to: {absolute_url}")
            page.goto(absolute_url, wait_until="networkidle", timeout=60000)

            for key, value in field_data.items():
                selector = f"[name='{key}']"
                if page.query_selector(selector):
                    if isinstance(value, str) and os.path.exists(value):
                        print(f"Uploading file for {key}")
                        page.set_input_files(selector, value)
                    else:
                        print(f"Filling {key} with {value}")
                        page.fill(selector, str(value))
                else:
                    print(f"Warning: Field {key} not found.")

            for _ in range(5):
                next_btn = page.query_selector("button.next, input.next")
                submit_btn = page.query_selector("button[type='submit'], input[type='submit']")
                if next_btn:
                    print("Clicking Next button")
                    next_btn.click()
                    page.wait_for_load_state("networkidle")
                elif submit_btn:
                    print("Clicking Submit button")
                    submit_btn.click()
                    page.wait_for_load_state("networkidle")
                    break
                else:
                    print("No Next or Submit button found")
                    break

            with open("submission_log.json", "a") as f:
                json.dump({
                    "url": url,
                    "data": dict(field_data),
                    "timestamp": str(os.path.getctime(url) if os.path.exists(url) else os.path.getctime(__file__))
                }, f)
                f.write("\n")

            print("Form submission data saved to submission_log.json")

        except Exception as e:
            print(f"Error during form submission: {str(e)}")
            raise
        finally:
            browser.close()
            print("Browser closed")
