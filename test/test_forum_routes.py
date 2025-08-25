import time

def test_post_and_get_question_success(client):
    payload = {
        "title": "Integration Test Question",
        "body": "This is a real integration test.",
        "tags": ["integration", "pytest"]
    }

    response = client.post(
        "/questions",
        json=payload,
        headers={"X-User-Id": "real-user"}
    )

    data = response.get_json()
    qid = data["qid"]

    response2 = client.get(f"/questions/{qid}")
    data2 = response2.get_json()

    # Check response
    assert response.status_code == 201
    assert "qid" in data
    assert data2["title"] == payload["title"]
    assert data2["body"] == payload["body"]
    assert data2["tags"] == payload["tags"]

def test_post_question_validation_error(client):
    # Invalid: title too short
    payload = {"title": "", "body": "bad", "tags": []}

    response = client.post(
        "/questions",
        json=payload,
        headers={"X-User-Id": "real-user"}
    )

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "validation"
