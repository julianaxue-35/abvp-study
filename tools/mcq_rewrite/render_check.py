"""usage: python3 render_check.py page.html ... -> loads each page in headless Chrome, opens the MCQ tab, clicks first answers, reports JS errors + card count."""
import sys, pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parents[2]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless=True)
    for f in sys.argv[1:]:
        pg = b.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:150]))
        pg.goto((ROOT / f).as_uri()); pg.wait_for_timeout(300)
        btn = pg.query_selector('button[data-p="mcq"]')
        if btn: btn.click(); pg.wait_for_timeout(200)
        cards = pg.query_selector_all("#mcq .q, #mcq .qcard, #mcq [data-tag], #mcq .card")
        opts = pg.query_selector_all("#mcq .opt")
        print(f, "| cards", len(cards), "| option buttons", len(opts), "| errors", errs or "none")
        pg.close()
    b.close()
