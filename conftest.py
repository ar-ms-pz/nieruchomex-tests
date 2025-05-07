import random
import pytest
import requests
from playwright.sync_api import Page

API_URL = "http://localhost:3000"
PAGE_URL = "http://localhost:5173/"


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
    def create_user(method="api", user_type="user"):
        user_number = enumerating()
        payload = {
            "name": f"test_{user_type}{user_number}",
            "email": f"test_{user_type}{user_number}@nieruchomex.pl",
            "phone": f"{random.randrange(111111111, 999999999)}",
            "password": "zaq1@WSX"
        }
        if method == "api" and user_type == "user":
            r = requests.post(f"{API_URL}/auth/register", json=payload)
            if not r.status_code == requests.codes.ok:
                raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
        elif method == "ui" and user_type == "user":
            page.goto(PAGE_URL)
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
            page.get_by_role("button", name="Sign up").click()
        elif method == "api" and user_type == "admin":
            payload["type"] = "ADMIN"
            admin_creds = {
                "username": "admin",
                "password": payload["password"]
            }
            r = requests.post(f"{API_URL}/auth/login", json=admin_creds)
            if not r.status_code == requests.codes.ok:
                raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
            cookie = r.cookies.get_dict()
            r = requests.post(f"{API_URL}/users", json=payload, cookies=cookie)
            if not r.status_code == requests.codes.ok:
                raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
        elif method == "ui" and user_type == "admin":
            page.goto(PAGE_URL)
            page.get_by_role("link", name="Sign in").click()
            page.get_by_role("textbox", name="Username").click()
            page.get_by_role("textbox", name="Username").fill("admin")
            page.get_by_role("textbox", name="Password").click()
            page.get_by_role("textbox", name="Password").fill(payload["password"])
            page.get_by_role("button", name="Sign in").click()
            page.get_by_role("button", name="A", exact=True).click()
            page.get_by_role("menuitem", name="Admin Panel").click()
            page.get_by_role("button", name="Create User").click()
            page.get_by_role("combobox").click()
            page.get_by_role("option", name="Admin").click()
            page.get_by_role("textbox", name="Username").click()
            page.get_by_role("textbox", name="Username").fill(payload["name"])
            page.get_by_role("textbox", name="Password").click()
            page.get_by_role("textbox", name="Password").fill(payload["name"])
            page.get_by_role("textbox", name="Email").click()
            page.get_by_role("textbox", name="Email").fill(f"{payload["name"]}@nieruchomex.pl")
            page.get_by_role("textbox", name="Phone number").click()
            page.get_by_role("textbox", name="Phone number").fill(f"{random.randrange(111111111, 999999999)}")
            page.get_by_role("button", name="Create user").click()
        else:
            raise ValueError(f"Unknown user creation method: {method}")
        return {"username": payload["name"], "password": payload["password"]}
    return create_user


@pytest.fixture
def post_factory(enumerating):
    created_posts = []
    def create_post(test_user, params: dict):
        post_number = enumerating()
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
            "rooms": params.get("rooms", "1"),
            "area": params.get("area", "1"),
            "price": params.get("price", "1"),
            "type": params.get("type", "SALE"),
            "address": params.get("address", "Gabriela Narutowicza 11/12, 80-233 Gdańsk"),
            "longitude": params.get("longitude", "18.61323725767105"),
            "latitude": params.get("latitude", "54.37101387350977")
        }
        p = requests.post(f"{API_URL}/posts", json=payload, cookies=cookie)
        if not p.status_code == requests.codes.created:
            raise RuntimeError(f"Request error: {p.status_code} - {p.reason}")
        post = p.json()["data"]
        created_posts.append(post["id"])
        return post, cookie

    yield create_post
    
    for post_id in created_posts:
        r = requests.delete(f"{API_URL}/posts/{post_id}", cookies=cookie)
        if not r.status_code == requests.codes.ok:
            raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")


@pytest.fixture()
def delete_posts(enumerating, create_user_api):
    yield
    payload = {
        "username": create_user_api["username"],
        "password": create_user_api["password"]
    }
    r = requests.post(f"{API_URL}/auth/login", json=payload)
    if not r.status_code == requests.codes.ok:
        raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
    cookie = r.cookies.get_dict()
    r = requests.get(f"{API_URL}/posts", params={"status": "DRAFT"})
    if not r.status_code == requests.codes.ok:
        raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
    test_posts = []
    for p in r.json()["data"]:
        if p["title"].startswith("test_"):
            test_posts.append(p)
    for t_posts in test_posts:
        r = requests.delete(f"{API_URL}/posts/{t_posts["id"]}", cookies=cookie)
        if not r.status_code == requests.codes.ok:
            raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")


@pytest.fixture()
def delete_all_users():
    yield
    payload = {
        "username": "admin",
        "password": "zaq1@WSX"
    }
    r = requests.post(f"{API_URL}/auth/login", json=payload)
    if not r.status_code == requests.codes.ok:
        raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
    cookie = r.cookies.get_dict()
    r = requests.get(f"{API_URL}/users", cookies=cookie)
    if not r.status_code == requests.codes.ok:
        raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
    test_users = []
    for u in r.json()["data"]:
        if u["name"].startswith("test_"):
            test_users.append(u)
    for t_user in test_users:
        r = requests.delete(f"{API_URL}/users/{t_user["id"]}", cookies=cookie)
        if not r.status_code == requests.codes.ok:
            raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
