import pytest
from uuid import uuid4

def test_get_owners_empty(client, admin_token):
    response = client.get(
        "/v1/admin/accounts/owners",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"] == []

def test_get_washers_empty(client, admin_token):
    response = client.get(
        "/v1/admin/accounts/washers",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"] == []

def test_restrict_account_not_found(client, admin_token):
    random_id = str(uuid4())
    response = client.post(
        f"/v1/admin/accounts/restrict/{random_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"

def test_activate_account_not_found(client, admin_token):
    random_id = str(uuid4())
    response = client.post(
        f"/v1/admin/accounts/activate/{random_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"
