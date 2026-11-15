
def test_home_redirects_to_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_signup_page_loads(client):
    response = client.get("/signup")
    assert response.status_code == 200


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_user_can_sign_up(client):
    response = client.post(
        "/signup",
        data={
            "username": "testuser",
            "password": "testpass123",
            "confirm_password": "testpass123"
        }
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_user_can_log_in(client):
    client.post(
        "/signup",
        data={
            "username": "testuser",
            "password": "testpass123",
            "confirm_password": "testpass123"
        }
    )

    response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "testpass123"
        }
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
