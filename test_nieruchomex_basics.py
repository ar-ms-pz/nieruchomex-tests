import re
from playwright.sync_api import Page, expect
from conftest import PAGE_URL

expect.set_options(timeout=10_000)

def test_title(page: Page):
    page.goto(PAGE_URL)
    expect(page).to_have_title(re.compile("Nieruchomex"))


def test_logo_and_buttons(page: Page):
    page.goto(PAGE_URL)
    expect(page.get_by_test_id("home-logo-link"), "Home logo-link should be visible").to_be_visible()
    page.get_by_test_id("home-logo-link").click()
    assert page.url == PAGE_URL, "Home logo-link should point to home page"
    expect(page.get_by_test_id("sign-in-button"), "Sign in link should be visible").to_be_visible()
    expect(page.get_by_test_id("sign-up-button"), "Sign up link should be visible").to_be_visible()
    page.get_by_test_id("sign-in-button").click()
    assert page.url == f"{PAGE_URL}sign-in", "Sign in link should lead to PAGE_URL/sign_in"
    page.goto(PAGE_URL)
    page.get_by_test_id("sign-up-button").click()
    assert page.url == f"{PAGE_URL}sign-up", "Sign up link should lead to PAGE_URL/sign_up"


def test_themes(page: Page):
    page.goto(PAGE_URL)
    expect(page.get_by_role("button", name="Toggle theme"), "Toggle theme button should be visible").to_be_visible()
    page.get_by_role("button", name="Toggle theme").click()
    page.get_by_role("menuitemradio", name="Light").click()
    page.get_by_role("button", name="Toggle theme").click()
    expect(page.get_by_test_id("light-theme").locator("path"), "Chosen theme should be checked").to_be_visible()
    page.get_by_role("menuitemradio", name="Dark").click()
    page.get_by_role("button", name="Toggle theme").click()
    expect(page.get_by_test_id("dark-theme").locator("path"), "Chosen theme should be checked").to_be_visible()
    page.get_by_role("menuitemradio", name="System").click()
    page.get_by_role("button", name="Toggle theme").click()
    expect(page.get_by_test_id("system-theme").locator("path"), "Chosen theme should be checked").to_be_visible()


def test_languages(page: Page):
    page.goto(PAGE_URL)
    expect(page.get_by_role("button", name="Change language"), "Language change button should be visible").to_be_visible()
    page.get_by_role("button", name="Change language").click()
    page.get_by_test_id("lang-en").click()
    expect(page.get_by_test_id("home-search-header"), "Header should have english text").to_contain_text("What are you looking for?")
    page.get_by_role("button", name="Change language").click()
    page.get_by_test_id("lang-pl").click()
    expect(page.get_by_test_id("home-search-header"), "Header should have english text").to_contain_text("Czego dzisaj szukasz?")
