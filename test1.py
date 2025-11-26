from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth   # <-- Class import
import time

# ========= APNA DAAL =========
USERNAME = "iamsaniydv"
PASSWORD = "Sani@7255"
HEADLESS = False  # pehli baar False rakh
# ==============================

def invisipost_2025():
    with sync_playwright() as p:
        print(" 2025 ka sabse powerful free X poster chal raha hai!")

        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # Latest 2025 stealth apply (updated method name)
        stealth = Stealth()
        stealth.apply_stealth_sync(page)  # Updated method name

        page.set_default_timeout(120000)

        page.goto("https://x.com/home")
        time.sleep(10)

        page.fill('input[autocomplete="username"]', USERNAME)
        page.keyboard.press("Enter")
        time.sleep(10)

        page.wait_for_selector('input[name="password"]', timeout=40000)
        page.fill('input[name="password"]', PASSWORD)
        page.keyboard.press("Enter")
        time.sleep(15)

        # Verification aaye to manually daal de
        if page.locator('text=Verify your identity').is_visible(timeout=10000):
            print("⚠️ VERIFICATION AAYA – manually code daal de (90 sec)")
            time.sleep(90)

        page.wait_for_url("**/home", timeout=60000)
        print("✅ LOGIN HO GAYA BHAI!")

        page.click('a[href="/compose/tweet"]')
        time.sleep(6)

        page.fill('div[role="textbox"]', "Bhai finally latest playwright_stealth fix se post ho gaya! 🤖🔥\n21 November 2025 • Full free lifetime tool\n#InvisiPost #2025Working")
        time.sleep(3)

        page.click('div[data-testid="tweetButton"]')
        time.sleep(10)

        print("🎉 TWEET POST HO GAYA!!! X khol ke dekh 🔥🔥🔥🔥🔥🔥")

        context.storage_state(path="x_cookies.json")
        print("Cookies save – ab hamesha 10 second mein auto post!")

        browser.close()

if __name__ == "__main__":
    invisipost_2025()