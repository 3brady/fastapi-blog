import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, create_test_user, login_user


@pytest.mark.anyio
async def test_home_page(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Home" in response.text


@pytest.mark.anyio
async def test_posts_page_alias(client: AsyncClient):
    response = await client.get("/posts")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.anyio
async def test_static_pages(client: AsyncClient):
    pages = ["/login", "/register", "/account", "/forgot-password", "/reset-password"]
    for path in pages:
        response = await client.get(path)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


@pytest.mark.anyio
async def test_post_page(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)

    create_resp = await client.post(
        "/api/posts",
        json={"title": "Page Test Post", "content": "Testing template render"},
        headers=auth_header(token),
    )
    post_id = create_resp.json()["id"]

    response = await client.get(f"/post/{post_id}")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Page Test Post" in response.text

    not_found = await client.get("/post/99999")
    assert not_found.status_code == 404
    assert "text/html" in not_found.headers["content-type"]


@pytest.mark.anyio
async def test_user_posts_page(client: AsyncClient):
    user = await create_test_user(client)

    response = await client.get(f"/users/{user['id']}/posts")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert user["username"] in response.text

    not_found = await client.get("/users/99999/posts")
    assert not_found.status_code == 404
    assert "text/html" in not_found.headers["content-type"]
