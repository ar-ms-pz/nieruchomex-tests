import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    page.goto("http://localhost:5173/")

    # Expect page to have a title
    expect(page).to_have_title(re.compile("Nieruchomex"))