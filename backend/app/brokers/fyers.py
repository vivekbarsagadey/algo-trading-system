from fyers_apiv3 import fyersModel
from typing import Dict, Any, List, Optional
from .base import BrokerAdapter

class FyersBroker(BrokerAdapter):
    def __init__(self):
        self.fyers: Optional[fyersModel.FyersModel] = None
        self.client_id: Optional[str] = None

    async def connect(self, credentials: Dict[str, Any]) -> bool:
        self.client_id = credentials.get("client_id")
        access_token = credentials.get("access_token")
        
        # FyersModel initialization
        self.fyers = fyersModel.FyersModel(client_id=self.client_id, token=access_token, log_path="")
        
        # Verify connection by fetching profile
        # Note: fyersModel methods are synchronous.
        try:
            response = self.fyers.get_profile()
            if response.get("s") == "ok":
                return True
        except Exception:
            pass
        return False

    async def get_profile(self) -> Dict[str, Any]:
        if self.fyers:
            return self.fyers.get_profile()
        return {}

    async def place_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        if not self.fyers:
             raise RuntimeError("Broker not connected")

        # Map order types
        # Fyers: 1 => Limit, 2 => Market, 3 => Stop Limit, 4 => Stop Market
        order_type_map = {
            "LIMIT": 1,
            "MARKET": 2,
            "STOP_LIMIT": 3,
            "STOP_MARKET": 4
        }
        
        # Map side
        # Fyers: 1 => Buy, -1 => Sell
        side_map = {
            "BUY": 1,
            "SELL": -1
        }

        data = {
            "symbol": order_details.get("symbol"), # e.g. NSE:SBIN-EQ
            "qty": order_details.get("quantity"),
            "type": order_type_map.get(order_details.get("order_type", "MARKET"), 2),
            "side": side_map.get(order_details.get("side", "BUY"), 1),
            "productType": order_details.get("product_type", "INTRADAY"),
            "limitPrice": order_details.get("price", 0),
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
        }
        response = self.fyers.place_order(data)
        return response

    async def cancel_order(self, order_id: str) -> bool:
        if not self.fyers:
            return False
        data = {"id": order_id}
        response = self.fyers.cancel_order(data)
        return response.get("s") == "ok"

    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        if not self.fyers:
            return {}
        response = self.fyers.orderbook()
        if response.get("s") == "ok":
            for order in response.get("orderBook", []):
                if order["id"] == order_id:
                    return order
        return {}

    async def get_positions(self) -> List[Dict[str, Any]]:
        if not self.fyers:
            return []
        response = self.fyers.positions()
        if response.get("s") == "ok":
            return response.get("netPositions", [])
        return []

    async def get_holdings(self) -> List[Dict[str, Any]]:
        if not self.fyers:
            return []
        response = self.fyers.holdings()
        if response.get("s") == "ok":
            return response.get("holdings", [])
        return []
