import pytest
from httpx import AsyncClient
from tests.conftest import auth_header, create_test_user, login_user


@pytest.mark.anyio
async def test_get_post_empty(client: AsyncClient):
    response = await client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()

    assert data["posts"] == []
    assert data["total"] == 0
    assert data["has_more"] is False


@pytest.mark.anyio
async def test_get_post_not_found(client: AsyncClient):
    response = await client.get("/api/posts/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


@pytest.mark.anyio
async def test_create_post_success(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/api/posts",
        json={"title": "My First Post", "content": "This is the content"},
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My First Post"
    assert data["content"] == "This is the content"
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "date_posted" in data
    assert data["author"]["username"] == "testuser"


@pytest.mark.anyio
async def test_create_post_unauthorized(client: AsyncClient):
    response = await client.post(
        "/api/posts",
        json={"title": "Test Post", "content": "Test content"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_update_post_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/api/posts",
        json={"title": "Original Title", "content": "Original content"},
        headers=headers,
    )
    post_id = response.json()["id"]

    response = await client.patch(
        f"/api/posts/{post_id}",
        json={"title": "Updated Title"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Original content"


@pytest.mark.anyio
async def test_update_post_wrong_user(client: AsyncClient):
    await create_test_user(client, username="user1", email="user1@example.com")
    token1 = await login_user(client, email="user1@example.com")

    response = await client.post(
        "/api/posts",
        json={"title": "User 1's Post", "content": "Only user 1 can edit this"},
        headers=auth_header(token1),
    )
    post_id = response.json()["id"]

    await create_test_user(client, username="user2", email="user2@example.com")
    token2 = await login_user(client, email="user2@example.com")

    response = await client.patch(
        f"/api/posts/{post_id}",
        json={"title": "Hacked Title"},
        headers=auth_header(token2),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not Authorized to update this post"


@pytest.mark.anyio
async def test_get_posts_with_pagination(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    for i in range(5):
        response = await client.post(
            "/api/posts",
            json={"title": f"Post {i}", "content": f"Content for post {i}"},
            headers=headers,
        )
        assert response.status_code == 201

    response = await client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["posts"]) == 5
    assert data["has_more"] is False

    response = await client.get("/api/posts?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["posts"]) == 2
    assert data["has_more"] is True

    response = await client.get("/api/posts?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["posts"]) == 2
    assert data["skip"] == 2
    assert data["limit"] == 2


@pytest.mark.anyio
async def test_get_post_by_id_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    create_resp = await client.post(
        "/api/posts",
        json={"title": "Detail Post", "content": "Detail content"},
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    response = await client.get(f"/api/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == "Detail Post"
    assert data["content"] == "Detail content"
    assert data["author"]["username"] == "testuser"


@pytest.mark.anyio
async def test_update_post_full_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    create_resp = await client.post(
        "/api/posts",
        json={"title": "Old Title", "content": "Old content"},
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/posts/{post_id}",
        json={"title": "Completely New Title", "content": "Completely new content"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == "Completely New Title"
    assert data["content"] == "Completely new content"


@pytest.mark.anyio
async def test_delete_post_success(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    create_resp = await client.post(
        "/api/posts",
        json={"title": "To be deleted", "content": "Delete this"},
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    response = await client.delete(f"/api/posts/{post_id}", headers=headers)
    assert response.status_code == 204

    get_resp = await client.get(f"/api/posts/{post_id}")
    assert get_resp.status_code == 404


@pytest.mark.anyio
async def test_delete_post_unauthorized(client: AsyncClient):
    await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    create_resp = await client.post(
        "/api/posts",
        json={"title": "Protected Post", "content": "Delete protection test"},
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    response = await client.delete(f"/api/posts/{post_id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_delete_post_forbidden(client: AsyncClient):
    await create_test_user(client, username="owner", email="owner@example.com")
    owner_token = await login_user(client, email="owner@example.com")

    create_resp = await client.post(
        "/api/posts",
        json={"title": "Owner's Post", "content": "Belongs to owner"},
        headers=auth_header(owner_token),
    )
    post_id = create_resp.json()["id"]

    await create_test_user(client, username="intruder", email="intruder@example.com")
    intruder_token = await login_user(client, email="intruder@example.com")

    response = await client.delete(f"/api/posts/{post_id}", headers=auth_header(intruder_token))
    assert response.status_code == 403
    assert response.json()["detail"] == "Not Authorized to Delete this post"
