import time

from playwright.sync_api import Page, expect
from conftest import PAGE_URL, sign_in_ui, sign_out_ui, goto_wait

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

    sign_out_ui(page)

    assert sign_in_ui(test_user, page), "Cannot logon on user with changed password or data"

    page.get_by_test_id("user-nav-button").click()
    page.get_by_role("menuitem", name="My profile").click()

    expect(page.get_by_test_id("phone-input"), "Phone number did not change or changed to value other than test value").to_have_value(f"{NEW_PHONE}")
    expect(page.get_by_test_id("email-input"), "Email did not change or changed to value other than test value").to_have_value(f"changed_{test_user["email"]}")


def test_admin_user_permissions(page: Page, user_factory, post_factory):
    goto_wait(page, PAGE_URL)
    test_admin = user_factory(method="api", user_type="admin")

    assert test_admin is not None, "Cannot create test admin user"

    goto_wait(page, f"{PAGE_URL}/admin")
    assert sign_in_ui(test_admin, page), "Cannot logon crated admin user"
    expect(page.get_by_test_id("error-page-status-code"), "Cannot view admin panel").not_to_be_visible()

    test_post = post_factory(test_admin, params={"status": "PUBLISHED"})
    assert test_post is not None

    goto_wait(page, f"{PAGE_URL}/posts/{test_post["id"]}")
    page.get_by_role("link", name="Edit").click()
    expect(page.get_by_test_id("delete-post-button"), "Cannot delete created post").to_be_visible()

    sign_out_ui(page)
    test_user = user_factory(method="api", user_type="user")
    assert test_user is not None
    assert sign_in_ui(test_user, page)

    goto_wait(page, f"{PAGE_URL}/posts/{test_post["id"]}")
    expect(page.get_by_role("link", name="Edit"), "User can edit other user's post").not_to_be_visible()
