from typing import Any, Dict, List, Optional

import pyotp
from SmartApi import SmartConnect

from .base import BrokerAdapter


class AngelOneBroker(BrokerAdapter):
    def __init__(self):
        self.smart_api: Optional[SmartConnect] = None
        self.client_code: Optional[str] = None
        self.refresh_token: Optional[str] = None

    async def connect(self, credentials: Dict[str, Any]) -> bool:
        api_key = credentials.get("api_key")
        self.client_code = credentials.get("client_id")
        password = credentials.get("password")
        totp_key = credentials.get("totp_key")

        self.smart_api = SmartConnect(api_key=api_key)

        if totp_key:
            try:
                totp = pyotp.TOTP(totp_key).now()
            except Exception:
                totp = credentials.get("totp", "000000")
        else:
            totp = credentials.get("totp", "000000")

        # Note: generateSession is synchronous in the library usually,
        # but we are in an async method. It might block the loop briefly.
        # For production, run in executor.
        data = self.smart_api.generateSession(self.client_code, password, totp)

        if isinstance(data, dict):
            if data.get("status") is False:
                return False
            if "data" in data:
                self.refresh_token = data["data"].get("refreshToken")
                return True

        return True

    async def get_profile(self) -> Dict[str, Any]:
        if self.smart_api and self.refresh_token:
            return self.smart_api.getProfile(self.refresh_token)
        return {}

    async def place_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        if not self.smart_api:
            raise RuntimeError("Broker not connected")

        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": order_details.get("symbol"),
            "symboltoken": order_details.get("token"),  # Angel needs token
            "transactiontype": order_details.get("side"),
            "exchange": "NSE",
            "ordertype": order_details.get("order_type", "MARKET"),
            "producttype": order_details.get("product_type", "INTRADAY"),
            "duration": "DAY",
            "price": order_details.get("price", 0),
            "squareoff": "0",
            "stoploss": "0",
            "quantity": order_details.get("quantity"),
        }
        order_id = self.smart_api.placeOrder(orderparams)
        return {"order_id": order_id}

    async def cancel_order(self, order_id: str) -> bool:
        if not self.smart_api:
            return False
        try:
            self.smart_api.cancelOrder(order_id, "NORMAL")
            return True
        except Exception:
            return False

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        if not self.smart_api:
            return {}
        order_book = self.smart_api.orderBook()
        if order_book and "data" in order_book:
            for order in order_book["data"]:
                if order["orderid"] == order_id:
                    return order
        return {}

    async def get_positions(self) -> List[Dict[str, Any]]:
        if not self.smart_api:
            return []
        resp = self.smart_api.position()
        return resp.get("data", [])

    async def get_holdings(self) -> List[Dict[str, Any]]:
        if not self.smart_api:
            return []
        resp = self.smart_api.holding()
        return resp.get("data", [])
