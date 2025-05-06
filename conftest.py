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
def create_user_ui(page: Page, enumerating):
    user_number = enumerating()
    page.goto(PAGE_URL)
    page.get_by_role("link", name="Sign up").click()
    page.get_by_role("textbox", name="Username").click()
    page.get_by_role("textbox", name="Username").fill(f"test_user{user_number}")
    page.get_by_role("textbox", name="Email").click()
    page.get_by_role("textbox", name="Email").fill(f"test_user{user_number}@nieruchomex.pl")
    page.get_by_role("textbox", name="Phone number").click()
    page.get_by_role("textbox", name="Phone number").fill(f"{random.randrange(111111111,999999999)}")
    page.get_by_role("textbox", name="Password", exact=True).click()
    page.get_by_role("textbox", name="Password", exact=True).fill("zaq1@WSX")
    page.get_by_role("textbox", name="Confirm password").click()
    page.get_by_role("textbox", name="Confirm password").fill("zaq1@WSX")
    page.get_by_role("button", name="Sign up").click()


@pytest.fixture
def create_user_api(enumerating):
    user_number = enumerating()
    payload = {
        "username": f"test_user{user_number}",
        "email": f"test_user{user_number}@nieruchomex.pl",
        "phone": f"{random.randrange(111111111,999999999)}",
        "password": "zaq1@WSX"
    }
    r = requests.post(f"{API_URL}/auth/register", json=payload)
    if not r.status_code == requests.codes.ok:
        raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")


@pytest.fixture
def create_admin_ui(page: Page, enumerating):
    user_number = enumerating()
    page.goto(PAGE_URL)
    page.get_by_role("link", name="Sign in").click()
    page.get_by_role("textbox", name="Username").click()
    page.get_by_role("textbox", name="Username").fill("admin")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("zaq1@WSX")
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="A", exact=True).click()
    page.get_by_role("menuitem", name="Admin Panel").click()
    page.get_by_role("button", name="Create User").click()
    page.get_by_role("combobox").click()
    page.get_by_role("option", name="Admin").click()
    page.get_by_role("textbox", name="Username").click()
    page.get_by_role("textbox", name="Username").fill(f"test_admin{user_number}")
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill("zaq1@WSX")
    page.get_by_role("textbox", name="Email").click()
    page.get_by_role("textbox", name="Email").fill(f"test_admin{user_number}@nieruchomex.pl")
    page.get_by_role("textbox", name="Phone number").click()
    page.get_by_role("textbox", name="Phone number").fill(f"{random.randrange(111111111,999999999)}")
    page.get_by_role("button", name="Create user").click()


@pytest.fixture
def create_admin_api(enumerating):
    user_number = enumerating()
    payload = {
        "username": "admin",
        "password": "zaq1@WSX"
    }
    r = requests.post(f"{API_URL}/auth/login", json=payload)
    if not r.status_code == requests.codes.ok:
        raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
    cookie = r.cookies.get_dict()
    payload = {
        "email": f"test_admin{user_number}@mail.com",
        "name": f"test_admin{user_number}",
        "password": "zaq1@WSX",
        "phone": f"{random.randrange(111111111,999999999)}",
        "type": "ADMIN"
    }
    r = requests.post(f"{API_URL}/users", json=payload, cookies=cookie)
    if not r.status_code == requests.codes.ok:
        raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")


@pytest.fixture
def create_post_api(enumerating):
    number = enumerating()
    payload = {
        "username": f"test_user{number}",
        "password": "zaq1@WSX"
    }
    r = requests.post(f"{API_URL}/auth/login", json=payload)
    if not r.status_code == requests.codes.ok:
        raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
    cookie = r.cookies.get_dict()
    payload = {
        "title": f"test_post{number}",
        "description": f"test description on test_post{number}",
        "status": "DRAFT",
        "rooms": "1",
        "area": "1",
        "price": "1",
        "type": "SALE",
        "address": "Gabriela Narutowicza 4, 80-233 Gdańsk",
        "longitude": "45.666",
        "latitude": "54.996"
    }
    r = requests.post(f"{API_URL}/posts", json=payload, cookies=cookie)
    if not r.status_code == requests.codes.created:
        raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
    print(r.text)

@pytest.fixture(autouse=True)
def delete_users():
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


@pytest.fixture(autouse=True)
def delete_posts(enumerating):
    number = enumerating()
    yield
    payload = {
        "username": f"test_user{number}",
        "password": "zaq1@WSX"
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
        print(f"{API_URL}/posts/{t_posts["id"]}")
        r = requests.delete(f"{API_URL}/posts/{t_posts["id"]}", cookies=cookie)
        if not r.status_code == requests.codes.ok:
            raise RuntimeError(f"Request error: {r.status_code} - {r.reason}")
