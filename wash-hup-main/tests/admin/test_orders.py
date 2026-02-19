import pytest

def test_recommend_price(client, admin_token):
    response = client.post(
        "/v1/admin/orders/recommend-price",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    assert response.json()["message"] == "price added successfully"
    assert "data" in response.json()

def test_get_prices(client, admin_token):
    # First, ensure a price exists
    client.post(
        "/v1/admin/orders/recommend-price",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    response = client.get(
        "/v1/admin/orders/prices",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "quick_min" in response.json()["data"]

def test_get_orders_empty(client, admin_token):
    response = client.get(
        "/v1/admin/orders",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"] == []
