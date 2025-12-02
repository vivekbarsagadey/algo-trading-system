from .angel_one import AngelOneBroker
from .base import BrokerAdapter
from .dhan import DhanBroker
from .fyers import FyersBroker


def get_broker_adapter(broker_name: str) -> BrokerAdapter:
    """
    Factory function to get the appropriate broker adapter.
    """
    if broker_name.lower() == "dhan":
        return DhanBroker()
    if broker_name.lower() == "angelone":
        return AngelOneBroker()
    if broker_name.lower() == "fyers":
        return FyersBroker()
    raise ValueError(f"Unsupported broker: {broker_name}")


__all__ = ["BrokerAdapter", "DhanBroker", "AngelOneBroker", "FyersBroker", "get_broker_adapter"]
