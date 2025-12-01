from .base import BrokerAdapter
from .dhan import DhanBroker
from .angel_one import AngelOneBroker
from .fyers import FyersBroker

def get_broker_adapter(broker_name: str) -> BrokerAdapter:
    """
    Factory function to get the appropriate broker adapter.
    """
    if broker_name.lower() == "dhan":
        return DhanBroker()
    elif broker_name.lower() == "angelone":
        return AngelOneBroker()
    elif broker_name.lower() == "fyers":
        return FyersBroker()
    else:
        raise ValueError(f"Unsupported broker: {broker_name}")

__all__ = ["BrokerAdapter", "DhanBroker", "AngelOneBroker", "FyersBroker", "get_broker_adapter"]
