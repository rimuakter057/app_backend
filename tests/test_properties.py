from tests.conftest import auth_headers, register_and_login


def _create_draft_property(client, owner_token: str) -> dict:
    resp = client.post(
        "/api/v1/properties",
        json={
            "title": "Cozy Apartment",
            "kind": "rent",
            "type": "apartment",
            "price": 1200,
            "city": "Metropolis",
        },
        headers=auth_headers(owner_token),
    )
    assert resp.status_code == 201
    return resp.json()


def test_property_lifecycle_draft_to_active(client):
    owner_token = register_and_login(client, "owner@example.com", role="owner")
    admin_token = register_and_login(client, "admin@example.com", role="buyer")

    # Promote the second user to admin directly via the DB session used by the app,
    # since self-registering as admin is blocked by design.
    from app.core.database import get_db
    from app.crud.user import user as user_crud
    from app.main import app
    from app.models.enums import UserRole

    db_gen = app.dependency_overrides[get_db]()
    db = next(db_gen)
    admin_user = user_crud.get_by_email(db, "admin@example.com")
    admin_user.role = UserRole.admin
    db.add(admin_user)
    db.commit()

    prop = _create_draft_property(client, owner_token)
    assert prop["status"] == "draft"

    resp = client.get(f"/api/v1/properties/{prop['id']}", headers=auth_headers(owner_token))
    assert resp.status_code == 200

    resp = client.post(f"/api/v1/properties/{prop['id']}/submit", headers=auth_headers(owner_token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "pending"

    resp = client.post(f"/api/v1/admin/properties/{prop['id']}/approve", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"

    resp = client.get("/api/v1/properties")
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert prop["id"] in ids


def test_only_owner_can_submit_property(client):
    owner_token = register_and_login(client, "owner2@example.com", role="owner")
    other_owner_token = register_and_login(client, "owner3@example.com", role="owner")

    prop = _create_draft_property(client, owner_token)

    resp = client.post(f"/api/v1/properties/{prop['id']}/submit", headers=auth_headers(other_owner_token))
    assert resp.status_code == 403


def test_favorite_toggle_is_idempotent(client):
    owner_token = register_and_login(client, "owner4@example.com", role="owner")
    buyer_token = register_and_login(client, "buyer@example.com", role="buyer")
    prop = _create_draft_property(client, owner_token)

    resp = client.post(f"/api/v1/favorites/{prop['id']}", headers=auth_headers(buyer_token))
    assert resp.status_code == 201
    resp = client.post(f"/api/v1/favorites/{prop['id']}", headers=auth_headers(buyer_token))
    assert resp.status_code == 201

    resp = client.get("/api/v1/favorites", headers=auth_headers(buyer_token))
    assert resp.json()["total"] == 1

    resp = client.delete(f"/api/v1/favorites/{prop['id']}", headers=auth_headers(buyer_token))
    assert resp.status_code == 200
    resp = client.delete(f"/api/v1/favorites/{prop['id']}", headers=auth_headers(buyer_token))
    assert resp.status_code == 200

    resp = client.get("/api/v1/favorites", headers=auth_headers(buyer_token))
    assert resp.json()["total"] == 0
