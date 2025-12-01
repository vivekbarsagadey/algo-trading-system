import httpx
from typing import Dict, Any, List, Optional
from .base import BrokerAdapter


class DhanBroker(BrokerAdapter):
    BASE_URL = "https://api.dhan.co"

    def __init__(self):
        self.client_id: Optional[str] = None
        self.access_token: Optional[str] = None
        self.headers: Dict[str, str] = {}

    async def connect(self, credentials: Dict[str, Any]) -> bool:
        self.client_id = credentials.get("client_id")
        self.access_token = credentials.get("access_token")

        if not self.client_id or not self.access_token:
            return False

        self.headers = {"X-Client-Id": self.client_id, "X-Dhan-Client-Token": self.access_token, "Content-Type": "application/json"}
        # Ideally verify connection here
        return True

    async def get_profile(self) -> Dict[str, Any]:
        # Dhan doesn't have a simple profile endpoint in the snippet,
        # but we can assume standard implementation or skip for now.
        return {"client_id": self.client_id}

    async def place_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            payload = {
                "dhanClientId": self.client_id,
                "transactionType": order_details.get("side"),  # BUY/SELL
                "exchangeSegment": "NSE_EQ",  # Default to NSE Equity
                "productType": order_details.get("product_type", "INTRADAY"),
                "securityId": order_details.get("symbol"),  # This needs to be the security ID, not symbol name usually
                "quantity": order_details.get("quantity"),
                "orderType": order_details.get("order_type", "MARKET"),
                "price": order_details.get("price", 0),
                "validity": "DAY",
            }

            response = await client.post(f"{self.BASE_URL}/orders", headers=self.headers, json=payload)
            if response.status_code != 200:
                return {"status": "error", "message": response.text}
            return response.json()

    async def cancel_order(self, order_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.BASE_URL}/orders/{order_id}", headers=self.headers)
            return response.status_code == 200

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/orders/{order_id}", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return {}

    async def get_positions(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/positions", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return []

    async def get_holdings(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/holdings", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return []
