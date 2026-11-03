"""
Tests for restocking API endpoints.
"""
from datetime import datetime, timedelta

import pytest

import main


@pytest.fixture(autouse=True)
def clear_restocking_orders():
    """Submitted orders live in module state, so reset them around every test."""
    main.restocking_orders.clear()
    yield
    main.restocking_orders.clear()


def order_payload(items, budget=100000):
    return {"budget": budget, "items": items}


class TestRestockingDemandData:
    """Test suite for the cost fields restocking relies on."""

    def test_demand_forecasts_include_cost_fields(self, client):
        """Test that every forecast has the fields the restocking page needs."""
        response = client.get("/api/demand")
        assert response.status_code == 200

        data = response.json()
        assert len(data) > 0

        for forecast in data:
            assert isinstance(forecast["unit_cost"], (int, float))
            assert forecast["unit_cost"] > 0
            assert isinstance(forecast["supplier_name"], str)
            assert forecast["supplier_name"]
            assert isinstance(forecast["lead_time_days"], int)
            assert forecast["lead_time_days"] > 0


class TestRestockingOrderEndpoints:
    """Test suite for submitting and listing restocking orders."""

    def test_get_restocking_orders_empty(self, client):
        """Test that no orders exist before any are submitted."""
        response = client.get("/api/restocking/orders")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_restocking_order(self, client):
        """Test submitting a valid order."""
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "WDG-001", "quantity": 450}]),
        )
        assert response.status_code == 201

        order = response.json()
        assert order["order_number"].startswith("RST-")
        assert order["status"].lower() == "processing"
        assert order["budget"] == 100000
        assert len(order["items"]) == 1

        item = order["items"][0]
        assert item["sku"] == "WDG-001"
        assert item["name"] == "Industrial Widget Type A"
        assert item["quantity"] == 450
        assert item["unit_cost"] == 12.5
        assert abs(item["line_total"] - 5625.0) < 0.01

    def test_restocking_order_total_calculation(self, client):
        """Test that the order total is the sum of its line totals."""
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([
                {"sku": "WDG-001", "quantity": 450},
                {"sku": "GSK-203", "quantity": 600},
            ]),
        )
        assert response.status_code == 201

        order = response.json()
        calculated_total = sum(item["quantity"] * item["unit_cost"] for item in order["items"])
        assert abs(order["total_value"] - calculated_total) < 0.01
        assert abs(order["total_value"] - (5625.0 + 4050.0)) < 0.01

    def test_restocking_lead_time_uses_longest_item(self, client):
        """Test that lead time is the longest lead time among the ordered items."""
        # GSK-203 has a 5 day lead time, VLV-506 has 12
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([
                {"sku": "GSK-203", "quantity": 10},
                {"sku": "VLV-506", "quantity": 10},
            ]),
        )
        assert response.status_code == 201
        assert response.json()["lead_time_days"] == 12

    def test_restocking_expected_delivery_matches_lead_time(self, client):
        """Test that expected delivery is order date plus lead time."""
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "GSK-203", "quantity": 10}]),
        )
        assert response.status_code == 201

        order = response.json()
        order_date = datetime.fromisoformat(order["order_date"])
        expected_delivery = datetime.fromisoformat(order["expected_delivery"])
        assert expected_delivery - order_date == timedelta(days=order["lead_time_days"])

    def test_restocking_uses_server_side_prices(self, client):
        """Test that a client-supplied price is ignored."""
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "WDG-001", "quantity": 10, "unit_cost": 0.01}]),
        )
        assert response.status_code == 201
        assert response.json()["items"][0]["unit_cost"] == 12.5

    def test_restocking_order_exactly_at_budget(self, client):
        """Test that an order costing exactly the budget is accepted."""
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "WDG-001", "quantity": 10}], budget=125),
        )
        assert response.status_code == 201

    def test_restocking_order_over_budget_rejected(self, client):
        """Test that an order costing more than the budget is rejected."""
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "WDG-001", "quantity": 10}], budget=124.99),
        )
        assert response.status_code == 400
        assert "budget" in response.json()["detail"].lower()
        assert client.get("/api/restocking/orders").json() == []

    def test_restocking_unknown_sku_rejected(self, client):
        """Test that an unknown SKU is rejected."""
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "NOPE-999", "quantity": 1}]),
        )
        assert response.status_code == 400
        assert "unknown sku" in response.json()["detail"].lower()

    def test_restocking_duplicate_sku_rejected(self, client):
        """Test that the same SKU twice in one order is rejected."""
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([
                {"sku": "WDG-001", "quantity": 1},
                {"sku": "WDG-001", "quantity": 2},
            ]),
        )
        assert response.status_code == 400
        assert "duplicate" in response.json()["detail"].lower()

    def test_restocking_empty_items_rejected(self, client):
        """Test that an order with no items is rejected."""
        response = client.post("/api/restocking/orders", json=order_payload([]))
        assert response.status_code == 400
        assert "detail" in response.json()

    @pytest.mark.parametrize("quantity", [0, -5])
    def test_restocking_non_positive_quantity_rejected(self, client, quantity):
        """Test that zero or negative quantities fail validation."""
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "WDG-001", "quantity": quantity}]),
        )
        assert response.status_code == 422

    @pytest.mark.parametrize("budget", [0, -100])
    def test_restocking_non_positive_budget_rejected(self, client, budget):
        """Test that zero or negative budgets fail validation."""
        response = client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "WDG-001", "quantity": 1}], budget=budget),
        )
        assert response.status_code == 422

    def test_submitted_orders_listed_newest_first(self, client):
        """Test that submitted orders appear in the list, newest first."""
        first = client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "WDG-001", "quantity": 1}]),
        ).json()
        second = client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "GSK-203", "quantity": 1}]),
        ).json()

        response = client.get("/api/restocking/orders")
        assert response.status_code == 200

        data = response.json()
        assert [o["id"] for o in data] == [second["id"], first["id"]]
        assert first["order_number"] != second["order_number"]

    def test_restocking_orders_do_not_affect_regular_orders(self, client):
        """Test that restocking orders stay out of /api/orders and dashboard figures."""
        orders_before = len(client.get("/api/orders").json())
        summary_before = client.get("/api/dashboard/summary").json()

        client.post(
            "/api/restocking/orders",
            json=order_payload([{"sku": "WDG-001", "quantity": 1}]),
        )

        assert len(client.get("/api/orders").json()) == orders_before
        assert client.get("/api/dashboard/summary").json() == summary_before
