---
goal: Phase 6 - Market Data Listener for Real-Time Price Monitoring
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Backend Engineering Team
status: Planned
tags: [backend, market-data, websocket, real-time, stop-loss]
---

# Phase 6: Market Data Listener

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Goal

**GOAL-006**: Implement WebSocket-based market data listener for real-time LTP and stop-loss monitoring

## Overview

This phase implements the market data listener that connects to broker WebSocket feeds for real-time Last Traded Price (LTP) updates. The listener monitors prices for all active strategies and triggers stop-loss orders when conditions are met.

---

## Prerequisites

- Phase 1-5 completed
- Broker SDK installed (Zerodha KiteConnect, Dhan, Fyers, Angel One)
- Understanding of WebSocket protocols

## Dependencies

```txt
kiteconnect>=5.0.0
dhanhq>=1.0.0
fyers-apiv3>=3.0.0
smartapi-python>=1.4.0
websocket-client>=1.0.0
```

---

## Implementation Tasks

### TASK-065: Create MarketDataListener Base Class

**File**: `backend/app/services/market_listener.py`

**Description**: Create abstract MarketDataListener base class for WebSocket connections.

**Acceptance Criteria**:
- [ ] Abstract base class pattern
- [ ] WebSocket connection lifecycle
- [ ] Message handling interface
- [ ] Reconnection logic
- [ ] Health check method

**Code Reference**:
```python
from abc import ABC, abstractmethod
from typing import Dict, Set, Callable, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class MarketDataListener(ABC):
    """Abstract base class for market data WebSocket listeners"""
    
    def __init__(self, user_id: str, broker_config: dict):
        self.user_id = user_id
        self.broker_config = broker_config
        self.subscribed_symbols: Set[str] = set()
        self.callbacks: Dict[str, Callable] = {}
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
    
    @abstractmethod
    async def connect(self):
        """Establish WebSocket connection"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close WebSocket connection"""
        pass
    
    @abstractmethod
    async def subscribe(self, symbols: Set[str]):
        """Subscribe to symbols for LTP updates"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, symbols: Set[str]):
        """Unsubscribe from symbols"""
        pass
    
    def register_callback(self, event: str, callback: Callable):
        """Register callback for specific event"""
        self.callbacks[event] = callback
    
    async def on_tick(self, symbol: str, ltp: float, timestamp: str):
        """Handle price tick"""
        if "on_tick" in self.callbacks:
            await self.callbacks["on_tick"](symbol, ltp, timestamp)
    
    async def on_connect(self):
        """Handle successful connection"""
        self.is_connected = True
        self.reconnect_attempts = 0
        logger.info(f"Market data connected for user {self.user_id}")
        if "on_connect" in self.callbacks:
            await self.callbacks["on_connect"]()
    
    async def on_disconnect(self, error: Exception = None):
        """Handle disconnection"""
        self.is_connected = False
        logger.warning(f"Market data disconnected for user {self.user_id}: {error}")
        if "on_disconnect" in self.callbacks:
            await self.callbacks["on_disconnect"](error)
    
    async def on_error(self, error: Exception):
        """Handle connection error"""
        logger.error(f"Market data error for user {self.user_id}: {error}")
        if "on_error" in self.callbacks:
            await self.callbacks["on_error"](error)
    
    async def reconnect(self):
        """Attempt to reconnect with exponential backoff"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"Max reconnect attempts reached for user {self.user_id}")
            return False
        
        self.reconnect_attempts += 1
        wait_time = 2 ** self.reconnect_attempts  # Exponential backoff
        
        logger.info(f"Reconnecting in {wait_time}s (attempt {self.reconnect_attempts})")
        await asyncio.sleep(wait_time)
        
        try:
            await self.connect()
            if self.subscribed_symbols:
                await self.subscribe(self.subscribed_symbols)
            return True
        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            return await self.reconnect()
    
    async def health_check(self) -> dict:
        """Check listener health"""
        return {
            "is_connected": self.is_connected,
            "subscribed_symbols": list(self.subscribed_symbols),
            "reconnect_attempts": self.reconnect_attempts
        }
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-066: Implement Zerodha KiteConnect WebSocket

**File**: `backend/app/services/listeners/zerodha_listener.py`

**Description**: Implement Zerodha-specific WebSocket listener using KiteConnect.

**Acceptance Criteria**:
- [ ] KiteTicker integration
- [ ] Token-based subscription
- [ ] Handle LTP mode
- [ ] Auto-reconnect on disconnect
- [ ] Instrument token resolution

**Code Reference**:
```python
from kiteconnect import KiteTicker
from typing import Set
from app.services.market_listener import MarketDataListener
import logging

logger = logging.getLogger(__name__)

class ZerodhaMarketListener(MarketDataListener):
    """Zerodha KiteConnect WebSocket listener"""
    
    def __init__(self, user_id: str, broker_config: dict):
        super().__init__(user_id, broker_config)
        self.kite_ticker: KiteTicker = None
        self.api_key = broker_config["api_key"]
        self.access_token = broker_config["access_token"]
        self.instrument_tokens: Dict[str, int] = {}  # symbol -> token mapping
    
    async def connect(self):
        """Connect to Kite WebSocket"""
        self.kite_ticker = KiteTicker(self.api_key, self.access_token)
        
        # Register callbacks
        self.kite_ticker.on_ticks = self._on_ticks
        self.kite_ticker.on_connect = self._on_connect_sync
        self.kite_ticker.on_close = self._on_close_sync
        self.kite_ticker.on_error = self._on_error_sync
        self.kite_ticker.on_reconnect = self._on_reconnect_sync
        
        # Connect (blocking call, run in thread)
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.kite_ticker.connect, True)  # threaded=True
    
    async def disconnect(self):
        """Disconnect from Kite WebSocket"""
        if self.kite_ticker:
            self.kite_ticker.close()
            self.kite_ticker = None
        self.is_connected = False
    
    async def subscribe(self, symbols: Set[str]):
        """Subscribe to symbols"""
        if not self.kite_ticker:
            raise ConnectionError("Not connected to Kite WebSocket")
        
        # Resolve symbols to instrument tokens
        tokens = []
        for symbol in symbols:
            token = await self._get_instrument_token(symbol)
            if token:
                tokens.append(token)
                self.instrument_tokens[symbol] = token
                self.subscribed_symbols.add(symbol)
        
        if tokens:
            self.kite_ticker.subscribe(tokens)
            self.kite_ticker.set_mode(self.kite_ticker.MODE_LTP, tokens)
            logger.info(f"Subscribed to {len(tokens)} instruments")
    
    async def unsubscribe(self, symbols: Set[str]):
        """Unsubscribe from symbols"""
        if not self.kite_ticker:
            return
        
        tokens = [self.instrument_tokens[s] for s in symbols if s in self.instrument_tokens]
        if tokens:
            self.kite_ticker.unsubscribe(tokens)
            for symbol in symbols:
                self.subscribed_symbols.discard(symbol)
                self.instrument_tokens.pop(symbol, None)
    
    async def _get_instrument_token(self, symbol: str) -> int | None:
        """Get instrument token for symbol from Zerodha"""
        from app.services.broker_service import get_broker_adapter
        
        adapter = await get_broker_adapter(self.user_id, "zerodha")
        instruments = adapter.get_instruments("NSE")
        
        for inst in instruments:
            if inst["tradingsymbol"] == symbol:
                return inst["instrument_token"]
        
        logger.warning(f"Instrument token not found for {symbol}")
        return None
    
    def _on_ticks(self, ws, ticks):
        """Sync callback for price ticks"""
        import asyncio
        for tick in ticks:
            token = tick["instrument_token"]
            ltp = tick["last_price"]
            
            # Find symbol from token
            symbol = None
            for sym, tok in self.instrument_tokens.items():
                if tok == token:
                    symbol = sym
                    break
            
            if symbol:
                asyncio.create_task(self.on_tick(symbol, ltp, tick.get("timestamp")))
    
    def _on_connect_sync(self, ws, response):
        """Sync callback for connection"""
        import asyncio
        asyncio.create_task(self.on_connect())
    
    def _on_close_sync(self, ws, code, reason):
        """Sync callback for close"""
        import asyncio
        asyncio.create_task(self.on_disconnect(Exception(f"Closed: {code} {reason}")))
    
    def _on_error_sync(self, ws, code, reason):
        """Sync callback for error"""
        import asyncio
        asyncio.create_task(self.on_error(Exception(f"Error: {code} {reason}")))
    
    def _on_reconnect_sync(self, ws, attempts_count):
        """Sync callback for reconnection"""
        logger.info(f"Kite WebSocket reconnecting, attempt {attempts_count}")
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-067: Implement Dhan WebSocket Listener

**File**: `backend/app/services/listeners/dhan_listener.py`

**Description**: Implement Dhan-specific WebSocket listener.

**Acceptance Criteria**:
- [ ] Dhan WebSocket integration
- [ ] Security ID subscription
- [ ] LTP parsing
- [ ] Auto-reconnect
- [ ] Error handling

**Code Reference**:
```python
from dhanhq import DhanFeed
from typing import Set
from app.services.market_listener import MarketDataListener
import logging

logger = logging.getLogger(__name__)

class DhanMarketListener(MarketDataListener):
    """Dhan WebSocket listener"""
    
    def __init__(self, user_id: str, broker_config: dict):
        super().__init__(user_id, broker_config)
        self.dhan_feed: DhanFeed = None
        self.client_id = broker_config["client_id"]
        self.access_token = broker_config["access_token"]
        self.security_ids: Dict[str, int] = {}  # symbol -> security_id mapping
    
    async def connect(self):
        """Connect to Dhan WebSocket"""
        self.dhan_feed = DhanFeed(
            self.client_id,
            self.access_token,
            on_connect=self._on_connect_callback,
            on_message=self._on_message_callback,
            on_close=self._on_close_callback,
            on_error=self._on_error_callback
        )
        
        # Start WebSocket
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.dhan_feed.connect)
    
    async def disconnect(self):
        """Disconnect from Dhan WebSocket"""
        if self.dhan_feed:
            self.dhan_feed.disconnect()
            self.dhan_feed = None
        self.is_connected = False
    
    async def subscribe(self, symbols: Set[str]):
        """Subscribe to symbols"""
        if not self.dhan_feed:
            raise ConnectionError("Not connected to Dhan WebSocket")
        
        # Convert symbols to security IDs
        for symbol in symbols:
            security_id = await self._get_security_id(symbol)
            if security_id:
                self.security_ids[symbol] = security_id
                self.subscribed_symbols.add(symbol)
        
        # Subscribe to instruments
        instruments = [
            (1, str(sid), "NSE_EQ")  # 1 = Quote mode
            for sid in self.security_ids.values()
        ]
        
        if instruments:
            self.dhan_feed.subscribe_symbols(instruments)
            logger.info(f"Subscribed to {len(instruments)} Dhan instruments")
    
    async def unsubscribe(self, symbols: Set[str]):
        """Unsubscribe from symbols"""
        if not self.dhan_feed:
            return
        
        instruments = [
            (1, str(self.security_ids[s]), "NSE_EQ")
            for s in symbols if s in self.security_ids
        ]
        
        if instruments:
            self.dhan_feed.unsubscribe_symbols(instruments)
            for symbol in symbols:
                self.subscribed_symbols.discard(symbol)
                self.security_ids.pop(symbol, None)
    
    async def _get_security_id(self, symbol: str) -> int | None:
        """Get security ID for symbol from Dhan"""
        from app.services.broker_service import get_broker_adapter
        
        adapter = await get_broker_adapter(self.user_id, "dhan")
        # Dhan-specific security ID lookup
        return adapter.get_security_id(symbol, "NSE")
    
    def _on_connect_callback(self):
        """Handle connection"""
        import asyncio
        asyncio.create_task(self.on_connect())
    
    def _on_message_callback(self, message):
        """Handle price message"""
        import asyncio
        
        # Parse Dhan message format
        if isinstance(message, dict) and "LTP" in message:
            security_id = message.get("security_id")
            ltp = message.get("LTP")
            
            # Find symbol from security ID
            symbol = None
            for sym, sid in self.security_ids.items():
                if sid == security_id:
                    symbol = sym
                    break
            
            if symbol:
                asyncio.create_task(self.on_tick(symbol, ltp, message.get("timestamp")))
    
    def _on_close_callback(self, code, reason):
        """Handle close"""
        import asyncio
        asyncio.create_task(self.on_disconnect(Exception(f"Closed: {code}")))
    
    def _on_error_callback(self, error):
        """Handle error"""
        import asyncio
        asyncio.create_task(self.on_error(error))
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-068: Implement LTP Cache in Redis

**File**: `backend/app/services/market_listener.py`

**Description**: Implement LTP caching in Redis for quick price lookups.

**Acceptance Criteria**:
- [ ] Cache LTP with TTL
- [ ] Fast lookup for stop-loss checks
- [ ] Update on each tick
- [ ] Handle stale prices
- [ ] Batch update support

**Code Reference**:
```python
from app.services.redis_service import get_redis, RedisKeys
from decimal import Decimal
import json
from datetime import datetime

LTP_CACHE_TTL = 30  # Seconds - LTP considered stale after this

async def update_ltp_cache(symbol: str, ltp: float, timestamp: str = None):
    """Update LTP in Redis cache"""
    redis = await get_redis()
    
    cache_data = {
        "ltp": str(ltp),
        "timestamp": timestamp or datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    key = RedisKeys.ltp(symbol)
    await redis.setex(key, LTP_CACHE_TTL, json.dumps(cache_data))

async def get_cached_ltp(symbol: str) -> Decimal | None:
    """Get LTP from Redis cache"""
    redis = await get_redis()
    
    key = RedisKeys.ltp(symbol)
    data = await redis.get(key)
    
    if data:
        parsed = json.loads(data)
        return Decimal(parsed["ltp"])
    
    return None

async def get_cached_ltp_with_timestamp(symbol: str) -> dict | None:
    """Get LTP with timestamp from Redis cache"""
    redis = await get_redis()
    
    key = RedisKeys.ltp(symbol)
    data = await redis.get(key)
    
    if data:
        parsed = json.loads(data)
        return {
            "ltp": Decimal(parsed["ltp"]),
            "timestamp": parsed["timestamp"],
            "is_stale": (datetime.utcnow() - datetime.fromisoformat(parsed["updated_at"])).seconds > LTP_CACHE_TTL
        }
    
    return None

async def batch_update_ltp(prices: Dict[str, float]):
    """Batch update LTPs in Redis"""
    redis = await get_redis()
    
    pipeline = redis.client.pipeline()
    timestamp = datetime.utcnow().isoformat()
    
    for symbol, ltp in prices.items():
        cache_data = json.dumps({
            "ltp": str(ltp),
            "timestamp": timestamp,
            "updated_at": timestamp
        })
        key = RedisKeys.ltp(symbol)
        pipeline.setex(key, LTP_CACHE_TTL, cache_data)
    
    await pipeline.execute()

async def get_all_cached_ltps(symbols: Set[str]) -> Dict[str, Decimal]:
    """Get LTPs for multiple symbols"""
    redis = await get_redis()
    
    result = {}
    for symbol in symbols:
        ltp = await get_cached_ltp(symbol)
        if ltp:
            result[symbol] = ltp
    
    return result
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-069: Implement Stop-Loss Monitor

**File**: `backend/app/services/stop_loss_monitor.py`

**Description**: Implement stop-loss monitoring that checks LTP against strategy stop-loss levels.

**Acceptance Criteria**:
- [ ] Monitor all active strategies with positions
- [ ] Trigger on LTP <= stop_loss
- [ ] Execute sell order immediately
- [ ] Prevent duplicate triggers
- [ ] Log all stop-loss events

**Code Reference**:
```python
from decimal import Decimal
from typing import List
import logging
from app.services.redis_service import (
    get_all_active_strategies,
    update_strategy_state,
    acquire_order_lock,
    LockAcquisitionError,
    publish_sl_triggered
)

logger = logging.getLogger(__name__)

class StopLossMonitor:
    """Monitors prices and triggers stop-loss orders"""
    
    def __init__(self):
        self.active_monitors: Dict[str, dict] = {}  # symbol -> strategies
    
    async def on_price_update(self, symbol: str, ltp: Decimal):
        """Called on each price tick"""
        # Get strategies for this symbol
        strategies = await self._get_strategies_for_symbol(symbol)
        
        for strategy in strategies:
            await self._check_stop_loss(strategy, ltp)
    
    async def _get_strategies_for_symbol(self, symbol: str) -> List[dict]:
        """Get active strategies with positions for a symbol"""
        from app.services.redis_service import get_active_strategies_by_symbol
        
        strategies = await get_active_strategies_by_symbol(symbol)
        
        # Filter: only those with BOUGHT position
        return [s for s in strategies if s.get("position") == "BOUGHT"]
    
    async def _check_stop_loss(self, strategy: dict, current_ltp: Decimal):
        """Check if stop-loss condition is met"""
        strategy_id = strategy["id"]
        user_id = strategy["user_id"]
        stop_loss = Decimal(str(strategy["stop_loss"]))
        
        # Check if SL already triggered
        if strategy.get("sl_triggered"):
            return
        
        # Check condition: LTP <= stop_loss
        if current_ltp <= stop_loss:
            logger.warning(
                f"STOP-LOSS TRIGGERED: Strategy {strategy_id}, "
                f"LTP {current_ltp} <= SL {stop_loss}"
            )
            
            await self._execute_stop_loss(strategy, current_ltp)
    
    async def _execute_stop_loss(self, strategy: dict, trigger_price: Decimal):
        """Execute stop-loss order"""
        strategy_id = strategy["id"]
        user_id = strategy["user_id"]
        
        try:
            # Acquire lock to prevent duplicate orders
            async with acquire_order_lock(strategy_id, "SL"):
                
                # Double-check SL not already triggered
                from app.services.redis_service import get_active_strategy
                latest = await get_active_strategy(strategy_id, user_id)
                if latest.get("sl_triggered"):
                    logger.info(f"SL already triggered for {strategy_id}")
                    return
                
                # Mark SL as triggered
                await update_strategy_state(
                    strategy_id,
                    user_id,
                    {
                        "sl_triggered": "true",
                        "sl_trigger_price": str(trigger_price)
                    }
                )
                
                # Execute sell order
                from app.services.execution_engine import place_sl_sell_order
                result = await place_sl_sell_order(strategy, trigger_price)
                
                # Publish event
                await publish_sl_triggered(user_id, strategy_id, float(trigger_price))
                
                logger.info(f"Stop-loss order executed for {strategy_id}: {result}")
                
        except LockAcquisitionError:
            logger.warning(f"Could not acquire SL lock for {strategy_id}, another process handling")
        except Exception as e:
            logger.error(f"Error executing stop-loss for {strategy_id}: {e}")
            raise

# Singleton instance
_sl_monitor: StopLossMonitor = None

def get_stop_loss_monitor() -> StopLossMonitor:
    global _sl_monitor
    if _sl_monitor is None:
        _sl_monitor = StopLossMonitor()
    return _sl_monitor
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-070: Implement Tick Processing Pipeline

**File**: `backend/app/services/market_listener.py`

**Description**: Implement tick processing pipeline: receive tick → update cache → check stop-loss.

**Acceptance Criteria**:
- [ ] Sequential processing per symbol
- [ ] Async processing across symbols
- [ ] Error isolation per tick
- [ ] Performance monitoring
- [ ] Backpressure handling

**Code Reference**:
```python
from decimal import Decimal
import asyncio
from typing import Dict
import time
import logging

logger = logging.getLogger(__name__)

class TickProcessor:
    """Processes incoming price ticks"""
    
    def __init__(self):
        self.processing_times: Dict[str, float] = {}
        self.tick_count = 0
        self.error_count = 0
    
    async def process_tick(self, symbol: str, ltp: float, timestamp: str = None):
        """Process a single tick"""
        start_time = time.time()
        
        try:
            ltp_decimal = Decimal(str(ltp))
            
            # Step 1: Update LTP cache
            await update_ltp_cache(symbol, ltp, timestamp)
            
            # Step 2: Check stop-loss
            sl_monitor = get_stop_loss_monitor()
            await sl_monitor.on_price_update(symbol, ltp_decimal)
            
            # Step 3: Broadcast to SSE subscribers (optional)
            await self._broadcast_price(symbol, ltp_decimal)
            
            self.tick_count += 1
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error processing tick for {symbol}: {e}")
        
        finally:
            processing_time = time.time() - start_time
            self.processing_times[symbol] = processing_time
            
            if processing_time > 0.1:  # Log slow processing
                logger.warning(f"Slow tick processing for {symbol}: {processing_time:.3f}s")
    
    async def process_batch(self, ticks: List[Dict]):
        """Process batch of ticks"""
        tasks = []
        for tick in ticks:
            task = self.process_tick(
                tick["symbol"],
                tick["ltp"],
                tick.get("timestamp")
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _broadcast_price(self, symbol: str, ltp: Decimal):
        """Broadcast price update to SSE subscribers"""
        from app.services.redis_service import get_redis
        
        redis = await get_redis()
        
        event = {
            "type": "PRICE_UPDATE",
            "symbol": symbol,
            "ltp": str(ltp),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to price channel
        await redis.publish(f"prices:{symbol}", json.dumps(event))
    
    def get_stats(self) -> dict:
        """Get processing statistics"""
        avg_time = sum(self.processing_times.values()) / len(self.processing_times) if self.processing_times else 0
        
        return {
            "total_ticks": self.tick_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.tick_count if self.tick_count > 0 else 0,
            "avg_processing_time_ms": avg_time * 1000,
            "symbols_tracked": len(self.processing_times)
        }

# Singleton
_tick_processor: TickProcessor = None

def get_tick_processor() -> TickProcessor:
    global _tick_processor
    if _tick_processor is None:
        _tick_processor = TickProcessor()
    return _tick_processor
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-071: Create Listener Manager

**File**: `backend/app/services/listener_manager.py`

**Description**: Create ListenerManager to manage multiple broker WebSocket connections.

**Acceptance Criteria**:
- [ ] Manage multiple listeners per user
- [ ] Start/stop listeners
- [ ] Handle broker-specific listeners
- [ ] Aggregate subscriptions
- [ ] Health monitoring

**Code Reference**:
```python
from typing import Dict, Set
import logging
from app.services.market_listener import MarketDataListener
from app.services.listeners.zerodha_listener import ZerodhaMarketListener
from app.services.listeners.dhan_listener import DhanMarketListener

logger = logging.getLogger(__name__)

class ListenerManager:
    """Manages market data listeners for all users"""
    
    def __init__(self):
        # user_id -> broker -> listener
        self.listeners: Dict[str, Dict[str, MarketDataListener]] = {}
        self.tick_processor = get_tick_processor()
    
    async def start_listener(
        self,
        user_id: str,
        broker: str,
        broker_config: dict
    ) -> MarketDataListener:
        """Start a market data listener for user"""
        
        # Create broker-specific listener
        listener = self._create_listener(user_id, broker, broker_config)
        
        # Register tick callback
        async def on_tick(symbol: str, ltp: float, timestamp: str):
            await self.tick_processor.process_tick(symbol, ltp, timestamp)
        
        listener.register_callback("on_tick", on_tick)
        
        # Connect
        await listener.connect()
        
        # Store listener
        if user_id not in self.listeners:
            self.listeners[user_id] = {}
        self.listeners[user_id][broker] = listener
        
        logger.info(f"Started {broker} listener for user {user_id}")
        return listener
    
    async def stop_listener(self, user_id: str, broker: str):
        """Stop a market data listener"""
        if user_id in self.listeners and broker in self.listeners[user_id]:
            listener = self.listeners[user_id][broker]
            await listener.disconnect()
            del self.listeners[user_id][broker]
            
            if not self.listeners[user_id]:
                del self.listeners[user_id]
            
            logger.info(f"Stopped {broker} listener for user {user_id}")
    
    async def stop_all_listeners(self, user_id: str):
        """Stop all listeners for a user"""
        if user_id in self.listeners:
            for broker, listener in list(self.listeners[user_id].items()):
                await listener.disconnect()
            del self.listeners[user_id]
            logger.info(f"Stopped all listeners for user {user_id}")
    
    async def subscribe_symbols(
        self,
        user_id: str,
        broker: str,
        symbols: Set[str]
    ):
        """Subscribe to symbols on a listener"""
        if user_id in self.listeners and broker in self.listeners[user_id]:
            listener = self.listeners[user_id][broker]
            await listener.subscribe(symbols)
        else:
            raise ValueError(f"No listener found for user {user_id}, broker {broker}")
    
    async def unsubscribe_symbols(
        self,
        user_id: str,
        broker: str,
        symbols: Set[str]
    ):
        """Unsubscribe from symbols"""
        if user_id in self.listeners and broker in self.listeners[user_id]:
            listener = self.listeners[user_id][broker]
            await listener.unsubscribe(symbols)
    
    def _create_listener(
        self,
        user_id: str,
        broker: str,
        broker_config: dict
    ) -> MarketDataListener:
        """Create broker-specific listener"""
        listeners = {
            "zerodha": ZerodhaMarketListener,
            "dhan": DhanMarketListener,
            # "fyers": FyersMarketListener,
            # "angelone": AngelOneMarketListener,
        }
        
        if broker not in listeners:
            raise ValueError(f"Unsupported broker: {broker}")
        
        return listeners[broker](user_id, broker_config)
    
    async def get_all_health(self) -> dict:
        """Get health status of all listeners"""
        health = {}
        for user_id, brokers in self.listeners.items():
            health[user_id] = {}
            for broker, listener in brokers.items():
                health[user_id][broker] = await listener.health_check()
        
        health["tick_processor"] = self.tick_processor.get_stats()
        return health

# Singleton
_listener_manager: ListenerManager = None

def get_listener_manager() -> ListenerManager:
    global _listener_manager
    if _listener_manager is None:
        _listener_manager = ListenerManager()
    return _listener_manager
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-072: Add Symbol Subscription Management

**File**: `backend/app/services/listener_manager.py`

**Description**: Add dynamic symbol subscription based on active strategies.

**Acceptance Criteria**:
- [ ] Auto-subscribe on strategy start
- [ ] Auto-unsubscribe on strategy stop
- [ ] Handle multiple strategies per symbol
- [ ] Reference counting for subscriptions
- [ ] Efficient subscription updates

**Code Reference**:
```python
from collections import defaultdict

class SubscriptionManager:
    """Manages symbol subscriptions with reference counting"""
    
    def __init__(self, listener_manager: ListenerManager):
        self.listener_manager = listener_manager
        # user_id -> symbol -> strategy_ids
        self.subscriptions: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
    
    async def on_strategy_started(
        self,
        user_id: str,
        broker: str,
        strategy_id: str,
        symbol: str
    ):
        """Handle strategy start - subscribe to symbol if needed"""
        
        # Add to reference count
        self.subscriptions[user_id][symbol].add(strategy_id)
        
        # If first strategy for this symbol, subscribe
        if len(self.subscriptions[user_id][symbol]) == 1:
            try:
                await self.listener_manager.subscribe_symbols(
                    user_id, broker, {symbol}
                )
                logger.info(f"Subscribed to {symbol} for user {user_id}")
            except ValueError:
                # No listener yet, need to start one
                from app.services.broker_service import get_broker_config
                config = await get_broker_config(user_id, broker)
                await self.listener_manager.start_listener(user_id, broker, config)
                await self.listener_manager.subscribe_symbols(
                    user_id, broker, {symbol}
                )
    
    async def on_strategy_stopped(
        self,
        user_id: str,
        broker: str,
        strategy_id: str,
        symbol: str
    ):
        """Handle strategy stop - unsubscribe if no other strategies need the symbol"""
        
        # Remove from reference count
        if strategy_id in self.subscriptions[user_id][symbol]:
            self.subscriptions[user_id][symbol].discard(strategy_id)
        
        # If no more strategies for this symbol, unsubscribe
        if not self.subscriptions[user_id][symbol]:
            await self.listener_manager.unsubscribe_symbols(
                user_id, broker, {symbol}
            )
            del self.subscriptions[user_id][symbol]
            logger.info(f"Unsubscribed from {symbol} for user {user_id}")
            
            # If no more symbols for user, stop listener
            if not self.subscriptions[user_id]:
                await self.listener_manager.stop_listener(user_id, broker)
                del self.subscriptions[user_id]
    
    def get_subscribed_symbols(self, user_id: str) -> Set[str]:
        """Get all subscribed symbols for a user"""
        return set(self.subscriptions.get(user_id, {}).keys())
    
    def get_strategy_count(self, user_id: str, symbol: str) -> int:
        """Get number of strategies subscribed to a symbol"""
        return len(self.subscriptions.get(user_id, {}).get(symbol, set()))

# Singleton
_subscription_manager: SubscriptionManager = None

def get_subscription_manager() -> SubscriptionManager:
    global _subscription_manager
    if _subscription_manager is None:
        _subscription_manager = SubscriptionManager(get_listener_manager())
    return _subscription_manager
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-073: Add WebSocket Health Monitoring

**File**: `backend/app/api/health.py`

**Description**: Add WebSocket health monitoring endpoint.

**Acceptance Criteria**:
- [ ] Check all listeners health
- [ ] Show connection status
- [ ] Show subscription count
- [ ] Show tick processing stats
- [ ] Alert on unhealthy listeners

**Code Reference**:
```python
@router.get("/websocket")
async def websocket_health():
    """Check WebSocket listeners health"""
    from app.services.listener_manager import get_listener_manager
    
    manager = get_listener_manager()
    health = await manager.get_all_health()
    
    # Determine overall status
    all_healthy = True
    for user_id, brokers in health.items():
        if user_id == "tick_processor":
            continue
        for broker, status in brokers.items():
            if not status.get("is_connected"):
                all_healthy = False
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "listeners": health
    }
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-074: Write Market Listener Tests

**File**: `backend/tests/test_market_listener.py`

**Description**: Write tests for market data listener and stop-loss monitoring.

**Acceptance Criteria**:
- [ ] Test tick processing
- [ ] Test LTP caching
- [ ] Test stop-loss detection
- [ ] Test subscription management
- [ ] Test reconnection logic
- [ ] Mock WebSocket connections

**Code Reference**:
```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal
from app.services.stop_loss_monitor import StopLossMonitor, get_stop_loss_monitor
from app.services.market_listener import update_ltp_cache, get_cached_ltp
from app.services.listener_manager import ListenerManager, SubscriptionManager

class TestLTPCache:
    
    @pytest.mark.asyncio
    async def test_update_and_get_ltp(self):
        """Test LTP caching"""
        symbol = "RELIANCE"
        ltp = 2650.50
        
        await update_ltp_cache(symbol, ltp)
        
        cached = await get_cached_ltp(symbol)
        assert cached == Decimal("2650.50")

class TestStopLossMonitor:
    
    @pytest.fixture
    def sl_monitor(self):
        return StopLossMonitor()
    
    @pytest.mark.asyncio
    async def test_stop_loss_triggered(self, sl_monitor):
        """Test stop-loss triggers when LTP <= stop_loss"""
        strategy = {
            "id": "str_123",
            "user_id": "usr_456",
            "symbol": "INFY",
            "stop_loss": "1500.00",
            "position": "BOUGHT"
        }
        
        with patch.object(sl_monitor, "_get_strategies_for_symbol") as mock_get:
            mock_get.return_value = [strategy]
            
            with patch.object(sl_monitor, "_execute_stop_loss") as mock_exec:
                mock_exec.return_value = None
                
                # Price above SL - should not trigger
                await sl_monitor.on_price_update("INFY", Decimal("1550"))
                mock_exec.assert_not_called()
                
                # Price at SL - should trigger
                await sl_monitor.on_price_update("INFY", Decimal("1500"))
                mock_exec.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_no_trigger_if_no_position(self, sl_monitor):
        """Test stop-loss does not trigger without position"""
        strategy = {
            "id": "str_123",
            "user_id": "usr_456",
            "symbol": "INFY",
            "stop_loss": "1500.00",
            "position": "NONE"  # No position
        }
        
        with patch.object(sl_monitor, "_get_strategies_for_symbol") as mock_get:
            mock_get.return_value = [strategy]
            
            with patch.object(sl_monitor, "_execute_stop_loss") as mock_exec:
                await sl_monitor.on_price_update("INFY", Decimal("1400"))
                mock_exec.assert_not_called()

class TestSubscriptionManager:
    
    @pytest.fixture
    def subscription_manager(self):
        mock_listener_manager = Mock(spec=ListenerManager)
        mock_listener_manager.subscribe_symbols = AsyncMock()
        mock_listener_manager.unsubscribe_symbols = AsyncMock()
        return SubscriptionManager(mock_listener_manager)
    
    @pytest.mark.asyncio
    async def test_first_strategy_subscribes(self, subscription_manager):
        """Test first strategy for symbol triggers subscription"""
        await subscription_manager.on_strategy_started(
            "usr_1", "zerodha", "str_1", "RELIANCE"
        )
        
        subscription_manager.listener_manager.subscribe_symbols.assert_called_once()
        assert "RELIANCE" in subscription_manager.get_subscribed_symbols("usr_1")
    
    @pytest.mark.asyncio
    async def test_second_strategy_no_duplicate_subscribe(self, subscription_manager):
        """Test second strategy for same symbol does not re-subscribe"""
        await subscription_manager.on_strategy_started(
            "usr_1", "zerodha", "str_1", "RELIANCE"
        )
        await subscription_manager.on_strategy_started(
            "usr_1", "zerodha", "str_2", "RELIANCE"
        )
        
        # Only one subscribe call
        assert subscription_manager.listener_manager.subscribe_symbols.call_count == 1
        # But two strategies counted
        assert subscription_manager.get_strategy_count("usr_1", "RELIANCE") == 2
    
    @pytest.mark.asyncio
    async def test_last_strategy_unsubscribes(self, subscription_manager):
        """Test last strategy removal unsubscribes from symbol"""
        await subscription_manager.on_strategy_started(
            "usr_1", "zerodha", "str_1", "RELIANCE"
        )
        await subscription_manager.on_strategy_stopped(
            "usr_1", "zerodha", "str_1", "RELIANCE"
        )
        
        subscription_manager.listener_manager.unsubscribe_symbols.assert_called_once()
        assert "RELIANCE" not in subscription_manager.get_subscribed_symbols("usr_1")
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/services/market_listener.py` | Create | Base listener and LTP cache |
| `backend/app/services/listeners/__init__.py` | Create | Package init |
| `backend/app/services/listeners/zerodha_listener.py` | Create | Zerodha WebSocket |
| `backend/app/services/listeners/dhan_listener.py` | Create | Dhan WebSocket |
| `backend/app/services/stop_loss_monitor.py` | Create | Stop-loss monitoring |
| `backend/app/services/listener_manager.py` | Create | Listener management |
| `backend/app/api/health.py` | Modify | Add WebSocket health |
| `backend/tests/test_market_listener.py` | Create | Unit tests |

---

## Environment Variables Required

```bash
# No additional env vars required - uses broker credentials from Phase 2
```

---

## Definition of Done

- [ ] All 10 tasks completed
- [ ] Zerodha and Dhan listeners working
- [ ] LTP caching working
- [ ] Stop-loss monitoring working
- [ ] Subscription management working
- [ ] Health monitoring working
- [ ] Unit tests passing
- [ ] Code reviewed and approved

---

## Next Phase

After completing Phase 6, proceed to [Phase 7: Execution Engine](./phase-07-execution-engine.md)
