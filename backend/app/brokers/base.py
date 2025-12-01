from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BrokerAdapter(ABC):
    """
    Abstract base class for all broker adapters.
    """

    @abstractmethod
    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """
        Establish connection with the broker using provided credentials.
        """
        pass

    @abstractmethod
    async def get_profile(self) -> Dict[str, Any]:
        """
        Get user profile information.
        """
        pass

    @abstractmethod
    async def place_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place an order.
        order_details should contain:
        - symbol: str
        - side: str (BUY/SELL)
        - quantity: int
        - product_type: str (INTRADAY/DELIVERY)
        - order_type: str (MARKET/LIMIT)
        - price: float (optional, for limit orders)
        """
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order.
        """
        pass

    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get the status of an order.
        """
        pass

    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current open positions.
        """
        pass

    @abstractmethod
    async def get_holdings(self) -> List[Dict[str, Any]]:
        """
        Get current holdings.
        """
        pass
