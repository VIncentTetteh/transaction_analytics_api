import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.routers.transactions import router
client = TestClient(app)

# Sample transaction data for tests
valid_transaction_data = {
    "user_id": "user123",
    "transaction_amount": 5000,
    "transaction_type": "DEBIT",
    "transaction_date": "2023-11-10T10:00:00Z"
}

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
@patch("app.routers.transactions.create_transaction", new_callable=AsyncMock)
@patch("app.routers.transactions.get_db", new_callable=AsyncMock)
async def test_create_transaction_route(mock_get_db, mock_create_transaction):
    # Set up mock response for create_transaction
    mock_create_transaction.return_value = TransactionResponse(
        id="transaction123",
        **valid_transaction_data,
        created_at="2023-11-10T10:00:00Z",
        updated_at="2023-11-10T10:00:00Z"
    )
    mock_get_db.return_value = mock_db  # Inject mock db dependency

    # Send POST request to create transaction
    response = client.post("/transactions/", json=valid_transaction_data)

    # Assert the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["transaction_amount"] == valid_transaction_data["transaction_amount"]
    assert response_data["transaction_type"] == valid_transaction_data["transaction_type"]
    assert response_data["user_id"] == valid_transaction_data["user_id"]

@pytest.mark.asyncio
@patch("app.routers.transactions.get_transaction", new_callable=AsyncMock)
@patch("app.routers.transactions.get_db", new_callable=AsyncMock)
async def test_get_transaction_route(mock_get_db, mock_get_transaction):
    transaction_id = "transaction123"
    mock_get_transaction.return_value = TransactionResponse(
        id=transaction_id,
        **valid_transaction_data,
        created_at="2023-11-10T10:00:00Z",
        updated_at="2023-11-10T10:00:00Z"
    )
    mock_get_db.return_value = mock_db

    # Send GET request to retrieve transaction
    response = client.get(f"/transactions/{transaction_id}")

    # Assert the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == transaction_id
    assert response_data["transaction_amount"] == valid_transaction_data["transaction_amount"]

@pytest.mark.asyncio
@patch("app.routers.transactions.update_transaction", new_callable=AsyncMock)
@patch("app.routers.transactions.get_db", new_callable=AsyncMock)
async def test_update_transaction_route(mock_get_db, mock_update_transaction):
    transaction_id = "transaction123"
    update_data = {"transaction_amount": 6000}

    mock_update_transaction.return_value = TransactionResponse(
        id=transaction_id,
        **valid_transaction_data,
        created_at="2023-11-10T10:00:00Z",
        updated_at="2023-11-10T10:00:00Z"
    )
    mock_get_db.return_value = mock_db

    # Send PUT request to update transaction
    response = client.put(f"/transactions/{transaction_id}", json=update_data)

    # Assert the response
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["transaction_amount"] == 6000

@pytest.mark.asyncio
@patch("app.routers.transactions.delete_transaction", new_callable=AsyncMock)
@patch("app.routers.transactions.get_db", new_callable=AsyncMock)
async def test_delete_transaction_route(mock_get_db, mock_delete_transaction):
    transaction_id = "transaction123"
    mock_delete_transaction.return_value = None
    mock_get_db.return_value = mock_db

    # Send DELETE request to remove transaction
    response = client.delete(f"/transactions/{transaction_id}")

    # Assert the response
    assert response.status_code == 204
    assert response.content == b""
