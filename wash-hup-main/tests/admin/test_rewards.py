import pytest

def test_create_reward(client, admin_token):
    reward_data = {
        "title": "New Reward",
        "rating_required": 4.5,
        "expiry_date": "2025-12-31T23:59:59"
    }
    response = client.post(
        "/v1/admin/rewards",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=reward_data
    )
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert response.json()["data"]["title"] == "New Reward"

def test_get_rewards(client, admin_token):
    response = client.get(
        "/v1/admin/rewards",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert isinstance(response.json()["data"], list)

def test_get_discounts_empty(client, admin_token):
    response = client.get(
        "/v1/admin/rewards/discounts",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"] == []
