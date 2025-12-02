from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BrokerAdapter(ABC):
    """
    Abstract base class for all broker adapters.
    """

    @abstractmethod
    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """
        Establish connection with the broker using provided credentials.
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_profile(self) -> Dict[str, Any]:
        """
        Get user profile information.
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order.
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get the status of an order.
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current open positions.
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_holdings(self) -> List[Dict[str, Any]]:
        """
        Get current holdings.
        """
        raise NotImplementedError()
