from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header, login_user, create_test_user


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "testuser",
        },
    )

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_create_user_duplicate_email(client: AsyncClient):
    await create_test_user(client)

    response = await client.post(
        "/api/users",
        json={
            "username": "different_user",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "email already exists"


@pytest.mark.anyio
async def test_create_user_success(client: AsyncClient):
    response = await client.post(
        "/api/users",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "image_path" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.anyio
async def test_upload_profile_picture(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    test_image_path = Path(__file__).parent / "test_image.jpg"
    image_bytes = test_image_path.read_bytes()

    response = await client.patch(
        f"/api/users/{user['id']}/picture",
        files={"file": ("profile.jpg", BytesIO(image_bytes), "image/jpeg")},
        headers=auth_header(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["image_file"] is not None
    assert data["image_file"].endswith(".jpg")
    assert "media/profile_pics" in data["image_path"]


@pytest.mark.anyio
async def test_forgot_password_sends_email(client: AsyncClient):
    await create_test_user(client)

    with patch(
            "routers.users.send_password_reset_email",
            new_callable=AsyncMock,
    ) as mock_send:
        response = await client.post(
            "/api/users/forgot-password",
            json={"email": "test@example.com"},
        )

        assert response.status_code == 202
        mock_send.assert_awaited_once()
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["to_email"] == "test@example.com"
        assert call_kwargs["username"] == "testuser"
        assert "token" in call_kwargs


@pytest.mark.anyio
async def test_get_current_user_me(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    response = await client.get("/api/users/me", headers=auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]


@pytest.mark.anyio
async def test_get_user_by_id(client: AsyncClient):
    user = await create_test_user(client)

    response = await client.get(f"/api/users/{user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user["id"]
    assert data["username"] == user["username"]
    assert "email" not in data

    not_found = await client.get("/api/users/99999")
    assert not_found.status_code == 404
    assert not_found.json()["detail"] == "user not found"


@pytest.mark.anyio
async def test_get_user_posts(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    empty_resp = await client.get(f"/api/users/{user['id']}/posts")
    assert empty_resp.status_code == 200
    assert empty_resp.json()["total"] == 0
    assert empty_resp.json()["posts"] == []

    await client.post(
        "/api/posts",
        json={"title": "User Post", "content": "Post content"},
        headers=headers,
    )

    response = await client.get(f"/api/users/{user['id']}/posts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["posts"]) == 1
    assert data["posts"][0]["title"] == "User Post"

    not_found = await client.get("/api/users/99999/posts")
    assert not_found.status_code == 404
    assert not_found.json()["detail"] == "User not found"


@pytest.mark.anyio
async def test_update_user_and_duplicate_checks(client: AsyncClient):
    user1 = await create_test_user(client, username="user1", email="user1@example.com")
    token1 = await login_user(client, email="user1@example.com")

    await create_test_user(client, username="user2", email="user2@example.com")

    resp = await client.patch(
        f"/api/users/{user1['id']}",
        json={"username": "updated_user1", "email": "updated1@example.com"},
        headers=auth_header(token1),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "updated_user1"
    assert data["email"] == "updated1@example.com"

    resp_dup_username = await client.patch(
        f"/api/users/{user1['id']}",
        json={"username": "user2"},
        headers=auth_header(token1),
    )
    assert resp_dup_username.status_code == 400
    assert resp_dup_username.json()["detail"] == "username already exists"

    resp_dup_email = await client.patch(
        f"/api/users/{user1['id']}",
        json={"email": "user2@example.com"},
        headers=auth_header(token1),
    )
    assert resp_dup_email.status_code == 400
    assert resp_dup_email.json()["detail"] == "email already registered"

    resp_forbidden = await client.patch(
        "/api/users/99999",
        json={"username": "hacked"},
        headers=auth_header(token1),
    )
    assert resp_forbidden.status_code == 403
    assert resp_forbidden.json()["detail"] == "Not authorized to update this user"


@pytest.mark.anyio
async def test_delete_user(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    resp_forbidden = await client.delete("/api/users/99999", headers=auth_header(token))
    assert resp_forbidden.status_code == 403
    assert resp_forbidden.json()["detail"] == "Not authorized to delete this user"

    resp_delete = await client.delete(f"/api/users/{user['id']}", headers=auth_header(token))
    assert resp_delete.status_code == 204

    resp_get = await client.get(f"/api/users/{user['id']}")
    assert resp_get.status_code == 404


@pytest.mark.anyio
async def test_reset_password_and_change_password(client: AsyncClient):
    user = await create_test_user(client, password="originalpassword123")

    captured_token = None
    with patch("routers.users.send_password_reset_email", new_callable=AsyncMock) as mock_send:
        await client.post("/api/users/forgot-password", json={"email": "test@example.com"})
        captured_token = mock_send.call_args.kwargs["token"]

    invalid_resp = await client.post(
        "/api/users/reset-password",
        json={"token": "invalid-token", "new_password": "newpassword123"},
    )
    assert invalid_resp.status_code == 400
    assert invalid_resp.json()["detail"] == "Invalid or expired reset token"

    reset_resp = await client.post(
        "/api/users/reset-password",
        json={"token": captured_token, "new_password": "newpassword123"},
    )
    assert reset_resp.status_code == 200
    assert "Password reset successfully" in reset_resp.json()["message"]

    new_token = await login_user(client, email="test@example.com", password="newpassword123")
    assert new_token is not None

    wrong_curr = await client.patch(
        "/api/users/me/password",
        json={"current_password": "wrongpassword", "new_password": "brandnewpassword123"},
        headers=auth_header(new_token),
    )
    assert wrong_curr.status_code == 400
    assert wrong_curr.json()["detail"] == "Current password is incorrect"

    change_resp = await client.patch(
        "/api/users/me/password",
        json={"current_password": "newpassword123", "new_password": "brandnewpassword123"},
        headers=auth_header(new_token),
    )
    assert change_resp.status_code == 200
    assert change_resp.json()["message"] == "Password Changed Successfully"

    latest_token = await login_user(client, email="test@example.com", password="brandnewpassword123")
    assert latest_token is not None


@pytest.mark.anyio
async def test_delete_user_picture(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)

    no_pic_resp = await client.delete(
        f"/api/users/{user['id']}/picture",
        headers=auth_header(token),
    )
    assert no_pic_resp.status_code == 400
    assert no_pic_resp.json()["detail"] == "No profile picture to Delete"

    test_image_path = Path(__file__).parent / "test_image.jpg"
    image_bytes = test_image_path.read_bytes()
    upload_resp = await client.patch(
        f"/api/users/{user['id']}/picture",
        files={"file": ("profile.jpg", BytesIO(image_bytes), "image/jpeg")},
        headers=auth_header(token),
    )
    assert upload_resp.status_code == 200
    assert upload_resp.json()["image_file"] is not None

    forbidden_resp = await client.delete(
        "/api/users/99999/picture",
        headers=auth_header(token),
    )
    assert forbidden_resp.status_code == 403

    delete_resp = await client.delete(
        f"/api/users/{user['id']}/picture",
        headers=auth_header(token),
    )
    assert delete_resp.status_code == 200
    assert delete_resp.json()["image_file"] is None


@pytest.mark.anyio
async def test_login_for_access_token_failures(client: AsyncClient):
    await create_test_user(client, email="test@example.com", password="correctpassword123")

    resp_wrong_pass = await client.post(
        "/api/users/token",
        data={"username": "test@example.com", "password": "wrongpassword"},
    )
    assert resp_wrong_pass.status_code == 401
    assert resp_wrong_pass.json()["detail"] == "incorrect email or password"

    resp_no_user = await client.post(
        "/api/users/token",
        data={"username": "nonexistent@example.com", "password": "anypassword"},
    )
    assert resp_no_user.status_code == 401
    assert resp_no_user.json()["detail"] == "incorrect email or password"
