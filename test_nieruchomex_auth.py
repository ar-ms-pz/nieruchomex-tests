import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page, user_factory, post_factory):
    page.goto("http://localhost:5173/")
    # Expect page to have a title
    expect(page).to_have_title(re.compile("Nieruchomex"))
def test_user_ui_post_create(user_factory, post_factory):
    test_user = user_factory(method="ui", user_type="user")
    assert test_user is not None
    test_post = post_factory(test_user, params={})
    assert test_post is not None
    test_user = user_factory(method="ui", user_type="admin")
    assert test_user is not None
    test_post = post_factory(test_user, params={})
    assert test_post is not None
def test_user_api_post_create(user_factory, post_factory):
    test_user = user_factory(method="api", user_type="user")
    assert test_user is not None
    test_post = post_factory(test_user, params={})
    assert test_post is not None
    test_user = user_factory(method="api", user_type="admin")
    assert test_user is not None
    test_post = post_factory(test_user, params={})
    assert test_post is not None

