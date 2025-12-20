import random
import time
import pytest
import requests
from playwright.sync_api import Page

API_URL = "https://api.nieruchomex.com/"
PAGE_URL = "https://nieruchomex.com/"

@pytest.fixture(scope="session")
def enumerating():
    number = 0
    def increment():
        nonlocal number
        number += 1
        return number
    return increment


@pytest.fixture
def user_factory(page: Page, enumerating):
    admin_creds = {
        "username": "admin",
        "password": "zaq1@WSX"
    }
    def create_user(method="api", user_type="user"):
        user_number = enumerating()
        nonlocal admin_creds
        payload = {
            "name": f"test_{user_type}{user_number}",
            "email": f"test_{user_type}{user_number}@nieruchomex.com",
            "phone": f"{random.randrange(111111111, 999999999)}",
            "password": "zaq1@WSX"
        }
        if method == "api" and user_type == "user":
            r = requests.post(f"{API_URL}/auth/register", json=payload)
            if not r.status_code == requests.codes.ok:
                raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
        elif method == "ui" and user_type == "user":
            goto_wait(page, PAGE_URL)
            page.get_by_role("link", name="Sign up").click()
            page.get_by_role("textbox", name="Username").click()
            page.get_by_role("textbox", name="Username").fill(payload["name"])
            page.get_by_role("textbox", name="Email").click()
            page.get_by_role("textbox", name="Email").fill(payload["email"])
            page.get_by_role("textbox", name="Phone number").click()
            page.get_by_role("textbox", name="Phone number").fill(payload["phone"])
            page.get_by_role("textbox", name="Password", exact=True).click()
            page.get_by_role("textbox", name="Password", exact=True).fill(payload["password"])
            page.get_by_role("textbox", name="Confirm password").click()
            page.get_by_role("textbox", name="Confirm password").fill(payload["password"])
            page.get_by_role("button", name="Submit").click()
            page.get_by_test_id("user-nav-button").click()
            page.get_by_role("menuitem", name="Sign out").click(timeout=10_000)
        elif method == "api" and user_type == "admin":
            payload["type"] = "ADMIN"
            r = requests.post(f"{API_URL}/auth/login", json=admin_creds)
            if not r.status_code == requests.codes.ok:
                raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
            cookie = r.cookies.get_dict()
            r = requests.post(f"{API_URL}/users", json=payload, cookies=cookie)
            if not r.status_code == requests.codes.ok:
                raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
        elif method == "ui" and user_type == "admin":
            goto_wait(page, PAGE_URL)
            page.get_by_role("link", name="Sign in").click()
            page.get_by_role("textbox", name="Username").click()
            page.get_by_role("textbox", name="Username").fill(admin_creds["username"])
            page.get_by_role("textbox", name="Password").click()
            page.get_by_role("textbox", name="Password").fill(admin_creds["password"])
            page.get_by_role("button", name="Submit").click()
            page.get_by_test_id("user-nav-button").click()
            page.get_by_role("menuitem", name="Admin panel").click()
            page.get_by_role("button", name="Create user").click()
            page.get_by_role("textbox", name="Username").click()
            page.get_by_role("textbox", name="Username").fill(payload["name"])
            page.get_by_role("textbox", name="Password").click()
            page.get_by_role("textbox", name="Password").fill(payload["password"])
            page.get_by_role("textbox", name="Email").click()
            page.get_by_role("textbox", name="Email").fill(payload["email"])
            page.get_by_role("textbox", name="Phone number").click()
            page.get_by_role("textbox", name="Phone number").fill(payload["phone"])
            page.get_by_role("combobox").click()
            page.get_by_role("option", name="Admin").click()
            page.get_by_role("button", name="Create user").click()
            page.get_by_test_id("user-nav-button").click()
            page.get_by_role("menuitem", name="Sign out").click()
        else:
            raise ValueError(f"Unknown user creation method: {method}")
        return {"username": payload["name"], "password": payload["password"], "email": payload["email"], "phone": payload["phone"]}

    yield create_user

    d = requests.post(f"{API_URL}/auth/login", json=admin_creds)
    if not d.status_code == requests.codes.ok:
        raise RuntimeError(f"Request error: {d.status_code} - {d.reason}")
    s_cookie = d.cookies.get_dict()
    d = requests.get(f"{API_URL}/users", cookies=s_cookie)
    if not d.status_code == requests.codes.ok:
        raise RuntimeError(f"Request error: {d.status_code} - {d.reason}")
    test_users = []
    for u in d.json()["data"]:
        if u["name"].startswith("test_"):
            test_users.append(u)
    for t_user in test_users:
        d = requests.delete(f"{API_URL}/users/{t_user["id"]}", cookies=s_cookie)
        if not d.status_code == requests.codes.ok:
            raise RuntimeError(f"Request error: {d.status_code} - {d.reason}")

@pytest.fixture
def post_factory(enumerating):
    def create_post(test_user, params: dict):
        post_number = enumerating()
        random_int = random.randrange(1, 2147483647)
        payload = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        p = requests.post(f"{API_URL}/auth/login", json=payload)
        if not p.status_code == requests.codes.ok:
            raise RuntimeError(f"Request error: {p.status_code} - {p.reason}")
        cookie = p.cookies.get_dict()
        payload = {
            "title": params.get("title", f"Test post number:{post_number}"),
            "description": params.get("description", f"Default description for test post {post_number}"),
            "status": params.get("status", "DRAFT"),
            "rooms": params.get("rooms", f"{random_int}"),
            "area": params.get("area", f"{random_int}"),
            "price": params.get("price", f"{random_int}"),
            "type": params.get("type", "SALE"),
            "address": params.get("address", "Gabriela Narutowicza 11/12, 80-233 Gdańsk"),
            "longitude": params.get("longitude", "18.61323725767105"),
            "latitude": params.get("latitude", "54.37101387350977")
        }
        p = requests.post(f"{API_URL}/posts", json=payload, cookies=cookie)
        if not p.status_code == requests.codes.created:
            raise RuntimeError(f"Request error: {p.status_code} - {p.reason}")
        post = p.json()["data"]
        return post
    return create_post


def sign_in_ui(user, page: Page) -> bool:
    goto_wait(page, PAGE_URL)
    page.get_by_test_id("sign-in-button").click()
    page.get_by_role("textbox", name="Username").click()
    page.get_by_role("textbox", name="Username").fill(f"{user["username"]}")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(f"{user["password"]}")
    page.get_by_role("button", name="Submit").click()
    if page.url == f"{PAGE_URL}/sign-in":
        return False
    else:
        return True


def sign_out_ui(page: Page):
    goto_wait(page, PAGE_URL)
    page.get_by_test_id("user-nav-button").click()
    page.get_by_role("menuitem", name="Sign out").click()


def goto_wait(page: Page, url):
    page.goto(url)
    time.sleep(1)
#new