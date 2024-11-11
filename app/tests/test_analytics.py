import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from datetime import date
from app.main import app  # Replace with the actual path to the main app instance

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
@patch("app.routers.analytics.AnalyticsService.get_average_transaction_value", new_callable=AsyncMock)
@patch("app.routers.analytics.get_db", new_callable=AsyncMock)
async def test_get_average_transaction_value(
    mock_get_db, mock_get_average_transaction_value, mock_db
):
    user_id = "user123"
    expected_average_value = 150.0  # GHC value to be returned by the mocked service

    mock_get_average_transaction_value.return_value = expected_average_value
    mock_get_db.return_value = mock_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/analytics/{user_id}/average_transaction_value")

    # Assert the response
    assert response.status_code == 200
    assert response.json() == expected_average_value

@pytest.mark.asyncio
@patch("app.routers.analytics.AnalyticsService.get_highest_transaction_day", new_callable=AsyncMock)
@patch("app.routers.analytics.get_db", new_callable=AsyncMock)
async def test_get_highest_transaction_day(
    mock_get_db, mock_get_highest_transaction_day, mock_db
):
    user_id = "user123"
    expected_highest_day = date(2023, 11, 10)  # Mocked date of the highest transaction day

    mock_get_highest_transaction_day.return_value = expected_highest_day
    mock_get_db.return_value = mock_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/analytics/{user_id}/highest_transaction_day")

    # Assert the response
    assert response.status_code == 200
    assert response.json() == {"highest_transaction_day": expected_highest_day.isoformat()}

@pytest.mark.asyncio
@patch("app.routers.analytics.AnalyticsService.get_transaction_totals", new_callable=AsyncMock)
@patch("app.routers.analytics.get_db", new_callable=AsyncMock)
async def test_get_transaction_totals(
    mock_get_db, mock_get_transaction_totals, mock_db
):
    user_id = "user123"
    start_date = date(2023, 11, 1)
    end_date = date(2023, 11, 10)
    expected_totals = {"debit_total": 1000.0, "credit_total": 2000.0}  # Expected totals in GHC

    mock_get_transaction_totals.return_value = expected_totals
    mock_get_db.return_value = mock_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/analytics/{user_id}/transaction_totals",
            params={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
        )

    # Assert the response
    assert response.status_code == 200
    assert response.json() == expected_totals