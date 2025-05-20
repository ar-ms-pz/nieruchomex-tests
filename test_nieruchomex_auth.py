import re

from playwright.sync_api import Page, expect
from conftest import PAGE_URL, sign_in_ui, sign_out_ui

expect.set_options(timeout=10_000)
NEW_PASSWORD = "zaq1@WSXcde3"
NEW_PHONE = "+48 100 123 100"

def test_user_change_data(page: Page, user_factory):
    test_user = user_factory(method="api", user_type="user")

    assert test_user is not None, "Cannot create user"
    assert sign_in_ui(test_user, page), "Cannot logon crated user"

    page.get_by_test_id("user-nav-button").click()
    page.get_by_role("menuitem", name="My profile").click()
    page.get_by_test_id("phone-input").click()
    page.get_by_test_id("phone-input").clear()
    page.get_by_test_id("phone-input").fill(NEW_PHONE)
    page.get_by_test_id("email-input").click()
    page.get_by_test_id("email-input").clear()
    page.get_by_test_id("email-input").fill(f"changed_{test_user["email"]}")
    page.get_by_test_id("password-input").click()
    page.get_by_test_id("password-input").fill(NEW_PASSWORD)
    page.get_by_role("button", name="Save").click()
    test_user["password"] = NEW_PASSWORD

    assert sign_out_ui(page), "Cannot sign out"

    assert sign_in_ui(test_user, page), "Cannot logon on user with changed password or data"

    page.get_by_test_id("user-nav-button").click()
    page.get_by_role("menuitem", name="My profile").click()

    expect(page.get_by_test_id("phone-input"), "Phone number did not change or changed to value other than test value").to_have_value(f"{NEW_PHONE}")
    expect(page.get_by_test_id("email-input"), "Email did not change or changed to value other than test value").to_have_value(f"changed_{test_user["email"]}")


#def test_admin_user_permissions(page: Page, user_factory, post_factory):
#    page.goto(PAGE_URL)
#    test_admin = user_factory(method="api", user_type="admin")
#
#    assert test_admin is not None, "Cannot create test admin user"
#    assert sign_in_ui(test_admin, page), "Cannot logon crated admin user"
#
#    page.goto(f"{PAGE_URL}/admin")
#    expect(page.get_by_text(re.compile("403")), "Logged user does not have permission to view admin panel").not_to_be_visible()


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

