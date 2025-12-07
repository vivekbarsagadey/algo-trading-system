---
goal: Phase 2 - Broker Integration Module
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Backend Engineering Team
status: Planned
tags: [backend, broker, zerodha, dhan, fyers, angel-one, encryption]
---

# Phase 2: Broker Integration Module

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Goal

**GOAL-002**: Implement secure multi-broker integration with Zerodha, Dhan, Fyers, and Angel One

## Overview

This phase implements broker integrations allowing users to connect their trading accounts. All broker credentials are encrypted with AES-256 before storage. The module supports multiple brokers through a factory pattern.

---

## Prerequisites

- Phase 1 (Authentication) completed
- Broker API documentation reviewed
- Test broker accounts created for each broker

## Dependencies

```txt
cryptography>=41.0.0
httpx>=0.25.0
kiteconnect>=4.2.0  # For Zerodha
```

---

## Implementation Tasks

### TASK-013: Create Abstract BaseBroker Class

**File**: `backend/app/brokers/base.py`

**Description**: Create abstract `BaseBroker` class defining the interface that all broker implementations must follow.

**Acceptance Criteria**:
- [ ] Abstract class with ABC
- [ ] `connect(credentials: dict) -> bool` - establish connection
- [ ] `validate() -> bool` - validate credentials are working
- [ ] `place_order(order: OrderRequest) -> OrderResponse` - place trading order
- [ ] `get_positions() -> List[Position]` - get current positions
- [ ] `get_ltp(symbol: str) -> float` - get last traded price
- [ ] `get_order_status(order_id: str) -> OrderStatus` - check order status
- [ ] Define common data models: OrderRequest, OrderResponse, Position, OrderStatus

**Code Reference**:
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class OrderRequest(BaseModel):
    symbol: str
    quantity: int
    side: OrderSide
    order_type: OrderType = OrderType.MARKET
    price: Optional[float] = None

class OrderResponse(BaseModel):
    order_id: str
    status: OrderStatus
    symbol: str
    quantity: int
    side: OrderSide
    price: Optional[float] = None
    message: Optional[str] = None

class Position(BaseModel):
    symbol: str
    quantity: int
    average_price: float
    current_price: float
    pnl: float

class BaseBroker(ABC):
    """Abstract base class for all broker implementations"""
    
    def __init__(self):
        self.is_connected = False
    
    @abstractmethod
    async def connect(self, api_key: str, api_secret: str, access_token: str) -> bool:
        """Establish connection with broker API"""
        pass
    
    @abstractmethod
    async def validate(self) -> bool:
        """Validate that credentials are working"""
        pass
    
    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place a trading order"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get current positions"""
        pass
    
    @abstractmethod
    async def get_ltp(self, symbol: str) -> float:
        """Get last traded price for symbol"""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> OrderStatus:
        """Get status of an order"""
        pass
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-014: Implement Zerodha Broker Integration

**File**: `backend/app/brokers/zerodha.py`

**Description**: Implement Zerodha broker using Kite Connect API with proper authentication.

**Acceptance Criteria**:
- [ ] Extends BaseBroker class
- [ ] Uses kiteconnect library
- [ ] Implements all abstract methods
- [ ] Handles API rate limits
- [ ] Proper error handling for API errors
- [ ] Supports equity segment orders

**Code Reference**:
```python
from kiteconnect import KiteConnect
from app.brokers.base import BaseBroker, OrderRequest, OrderResponse, Position, OrderStatus, OrderSide
import logging

logger = logging.getLogger(__name__)

class ZerodhaBroker(BaseBroker):
    """Zerodha Kite Connect implementation"""
    
    BROKER_TYPE = "zerodha"
    
    def __init__(self):
        super().__init__()
        self.kite: KiteConnect = None
    
    async def connect(self, api_key: str, api_secret: str, access_token: str) -> bool:
        try:
            self.kite = KiteConnect(api_key=api_key)
            self.kite.set_access_token(access_token)
            # Validate by fetching profile
            profile = self.kite.profile()
            logger.info(f"Connected to Zerodha as {profile['user_name']}")
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Zerodha connection failed: {e}")
            self.is_connected = False
            return False
    
    async def validate(self) -> bool:
        if not self.kite:
            return False
        try:
            self.kite.profile()
            return True
        except Exception:
            return False
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        try:
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=self.kite.EXCHANGE_NSE,
                tradingsymbol=order.symbol,
                transaction_type=self.kite.TRANSACTION_TYPE_BUY if order.side == OrderSide.BUY else self.kite.TRANSACTION_TYPE_SELL,
                quantity=order.quantity,
                product=self.kite.PRODUCT_MIS,
                order_type=self.kite.ORDER_TYPE_MARKET
            )
            return OrderResponse(
                order_id=str(order_id),
                status=OrderStatus.PENDING,
                symbol=order.symbol,
                quantity=order.quantity,
                side=order.side
            )
        except Exception as e:
            logger.error(f"Order placement failed: {e}")
            return OrderResponse(
                order_id="",
                status=OrderStatus.REJECTED,
                symbol=order.symbol,
                quantity=order.quantity,
                side=order.side,
                message=str(e)
            )
    
    async def get_positions(self) -> list[Position]:
        positions = self.kite.positions()
        result = []
        for pos in positions.get('day', []):
            if pos['quantity'] != 0:
                result.append(Position(
                    symbol=pos['tradingsymbol'],
                    quantity=pos['quantity'],
                    average_price=pos['average_price'],
                    current_price=pos['last_price'],
                    pnl=pos['pnl']
                ))
        return result
    
    async def get_ltp(self, symbol: str) -> float:
        quote = self.kite.ltp(f"NSE:{symbol}")
        return quote[f"NSE:{symbol}"]["last_price"]
    
    async def get_order_status(self, order_id: str) -> OrderStatus:
        orders = self.kite.orders()
        for order in orders:
            if str(order['order_id']) == order_id:
                status_map = {
                    'COMPLETE': OrderStatus.COMPLETE,
                    'REJECTED': OrderStatus.REJECTED,
                    'CANCELLED': OrderStatus.CANCELLED,
                    'OPEN': OrderStatus.OPEN,
                }
                return status_map.get(order['status'], OrderStatus.PENDING)
        return OrderStatus.PENDING
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-015: Implement Dhan Broker Integration

**File**: `backend/app/brokers/dhan.py`

**Description**: Implement Dhan broker integration with their REST API.

**Acceptance Criteria**:
- [ ] Extends BaseBroker class
- [ ] Uses httpx for API calls
- [ ] Implements all abstract methods
- [ ] Proper authentication headers
- [ ] Error handling for API responses

**Code Reference**:
```python
import httpx
from app.brokers.base import BaseBroker, OrderRequest, OrderResponse, Position, OrderStatus, OrderSide

class DhanBroker(BaseBroker):
    """Dhan API implementation"""
    
    BROKER_TYPE = "dhan"
    BASE_URL = "https://api.dhan.co"
    
    def __init__(self):
        super().__init__()
        self.client_id: str = None
        self.access_token: str = None
        self.http_client: httpx.AsyncClient = None
    
    async def connect(self, api_key: str, api_secret: str, access_token: str) -> bool:
        try:
            self.client_id = api_key  # Dhan uses client_id as api_key
            self.access_token = access_token
            self.http_client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "access-token": self.access_token,
                    "client-id": self.client_id,
                    "Content-Type": "application/json"
                }
            )
            # Validate connection
            is_valid = await self.validate()
            self.is_connected = is_valid
            return is_valid
        except Exception as e:
            self.is_connected = False
            return False
    
    async def validate(self) -> bool:
        try:
            response = await self.http_client.get("/fund-summary")
            return response.status_code == 200
        except Exception:
            return False
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        payload = {
            "transactionType": "BUY" if order.side == OrderSide.BUY else "SELL",
            "exchangeSegment": "NSE_EQ",
            "productType": "INTRADAY",
            "orderType": "MARKET",
            "tradingSymbol": order.symbol,
            "quantity": order.quantity,
        }
        response = await self.http_client.post("/orders", json=payload)
        data = response.json()
        
        if response.status_code == 200:
            return OrderResponse(
                order_id=data.get("orderId", ""),
                status=OrderStatus.PENDING,
                symbol=order.symbol,
                quantity=order.quantity,
                side=order.side
            )
        else:
            return OrderResponse(
                order_id="",
                status=OrderStatus.REJECTED,
                symbol=order.symbol,
                quantity=order.quantity,
                side=order.side,
                message=data.get("message", "Order failed")
            )
    
    async def get_positions(self) -> list[Position]:
        response = await self.http_client.get("/positions")
        positions = response.json()
        return [
            Position(
                symbol=pos["tradingSymbol"],
                quantity=pos["netQty"],
                average_price=pos["averagePrice"],
                current_price=pos["ltp"],
                pnl=pos["realizedProfit"] + pos["unrealizedProfit"]
            )
            for pos in positions if pos["netQty"] != 0
        ]
    
    async def get_ltp(self, symbol: str) -> float:
        response = await self.http_client.get(f"/market-quote/ltp?symbol={symbol}")
        return response.json()["ltp"]
    
    async def get_order_status(self, order_id: str) -> OrderStatus:
        response = await self.http_client.get(f"/orders/{order_id}")
        data = response.json()
        status_map = {
            "TRADED": OrderStatus.COMPLETE,
            "REJECTED": OrderStatus.REJECTED,
            "CANCELLED": OrderStatus.CANCELLED,
            "PENDING": OrderStatus.PENDING,
        }
        return status_map.get(data.get("orderStatus"), OrderStatus.PENDING)
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-016: Implement Fyers Broker Integration

**File**: `backend/app/brokers/fyers.py`

**Description**: Implement Fyers broker integration with OAuth flow handling.

**Acceptance Criteria**:
- [ ] Extends BaseBroker class
- [ ] Uses httpx for API calls
- [ ] Implements all abstract methods
- [ ] Handles OAuth access token
- [ ] Error handling for API responses

**Code Reference**:
```python
import httpx
from app.brokers.base import BaseBroker, OrderRequest, OrderResponse, Position, OrderStatus, OrderSide

class FyersBroker(BaseBroker):
    """Fyers API implementation"""
    
    BROKER_TYPE = "fyers"
    BASE_URL = "https://api.fyers.in/api/v2"
    
    def __init__(self):
        super().__init__()
        self.app_id: str = None
        self.access_token: str = None
        self.http_client: httpx.AsyncClient = None
    
    async def connect(self, api_key: str, api_secret: str, access_token: str) -> bool:
        try:
            self.app_id = api_key
            self.access_token = access_token
            self.http_client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"{self.app_id}:{self.access_token}",
                    "Content-Type": "application/json"
                }
            )
            is_valid = await self.validate()
            self.is_connected = is_valid
            return is_valid
        except Exception:
            self.is_connected = False
            return False
    
    async def validate(self) -> bool:
        try:
            response = await self.http_client.get("/profile")
            return response.status_code == 200 and response.json().get("s") == "ok"
        except Exception:
            return False
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        payload = {
            "symbol": f"NSE:{order.symbol}-EQ",
            "qty": order.quantity,
            "type": 2,  # Market order
            "side": 1 if order.side == OrderSide.BUY else -1,
            "productType": "INTRADAY",
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": "False",
        }
        response = await self.http_client.post("/orders", json=payload)
        data = response.json()
        
        if data.get("s") == "ok":
            return OrderResponse(
                order_id=data.get("id", ""),
                status=OrderStatus.PENDING,
                symbol=order.symbol,
                quantity=order.quantity,
                side=order.side
            )
        else:
            return OrderResponse(
                order_id="",
                status=OrderStatus.REJECTED,
                symbol=order.symbol,
                quantity=order.quantity,
                side=order.side,
                message=data.get("message", "Order failed")
            )
    
    async def get_positions(self) -> list[Position]:
        response = await self.http_client.get("/positions")
        data = response.json()
        if data.get("s") != "ok":
            return []
        return [
            Position(
                symbol=pos["symbol"].split(":")[1].replace("-EQ", ""),
                quantity=pos["qty"],
                average_price=pos["avgPrice"],
                current_price=pos["ltp"],
                pnl=pos["pl"]
            )
            for pos in data.get("netPositions", []) if pos["qty"] != 0
        ]
    
    async def get_ltp(self, symbol: str) -> float:
        response = await self.http_client.get(f"/quotes/?symbols=NSE:{symbol}-EQ")
        data = response.json()
        return data["d"][0]["v"]["lp"]
    
    async def get_order_status(self, order_id: str) -> OrderStatus:
        response = await self.http_client.get("/orders")
        data = response.json()
        for order in data.get("orderBook", []):
            if order["id"] == order_id:
                status_map = {
                    2: OrderStatus.COMPLETE,
                    1: OrderStatus.CANCELLED,
                    5: OrderStatus.REJECTED,
                }
                return status_map.get(order["status"], OrderStatus.PENDING)
        return OrderStatus.PENDING
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-017: Implement Angel One Broker Integration

**File**: `backend/app/brokers/angel_one.py`

**Description**: Implement Angel One SmartAPI integration.

**Acceptance Criteria**:
- [ ] Extends BaseBroker class
- [ ] Uses SmartAPI SDK or REST API
- [ ] Implements all abstract methods
- [ ] Handles TOTP/2FA if required
- [ ] Error handling for API responses

**Code Reference**:
```python
import httpx
from app.brokers.base import BaseBroker, OrderRequest, OrderResponse, Position, OrderStatus, OrderSide

class AngelOneBroker(BaseBroker):
    """Angel One SmartAPI implementation"""
    
    BROKER_TYPE = "angel_one"
    BASE_URL = "https://apiconnect.angelbroking.com"
    
    def __init__(self):
        super().__init__()
        self.api_key: str = None
        self.access_token: str = None
        self.http_client: httpx.AsyncClient = None
    
    async def connect(self, api_key: str, api_secret: str, access_token: str) -> bool:
        try:
            self.api_key = api_key
            self.access_token = access_token
            self.http_client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "X-UserType": "USER",
                    "X-SourceID": "WEB",
                    "X-ClientLocalIP": "127.0.0.1",
                    "X-ClientPublicIP": "127.0.0.1",
                    "X-MACAddress": "00:00:00:00:00:00",
                    "X-PrivateKey": self.api_key
                }
            )
            is_valid = await self.validate()
            self.is_connected = is_valid
            return is_valid
        except Exception:
            self.is_connected = False
            return False
    
    async def validate(self) -> bool:
        try:
            response = await self.http_client.get("/rest/secure/angelbroking/user/v1/getProfile")
            return response.status_code == 200 and response.json().get("status")
        except Exception:
            return False
    
    async def place_order(self, order: OrderRequest) -> OrderResponse:
        payload = {
            "variety": "NORMAL",
            "tradingsymbol": order.symbol,
            "symboltoken": "",  # Need to fetch from symbol master
            "transactiontype": "BUY" if order.side == OrderSide.BUY else "SELL",
            "exchange": "NSE",
            "ordertype": "MARKET",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "quantity": str(order.quantity),
        }
        response = await self.http_client.post(
            "/rest/secure/angelbroking/order/v1/placeOrder",
            json=payload
        )
        data = response.json()
        
        if data.get("status"):
            return OrderResponse(
                order_id=data["data"]["orderid"],
                status=OrderStatus.PENDING,
                symbol=order.symbol,
                quantity=order.quantity,
                side=order.side
            )
        else:
            return OrderResponse(
                order_id="",
                status=OrderStatus.REJECTED,
                symbol=order.symbol,
                quantity=order.quantity,
                side=order.side,
                message=data.get("message", "Order failed")
            )
    
    async def get_positions(self) -> list[Position]:
        response = await self.http_client.get(
            "/rest/secure/angelbroking/order/v1/getPosition"
        )
        data = response.json()
        if not data.get("status"):
            return []
        return [
            Position(
                symbol=pos["tradingsymbol"],
                quantity=int(pos["netqty"]),
                average_price=float(pos["averageprice"]),
                current_price=float(pos["ltp"]),
                pnl=float(pos["pnl"])
            )
            for pos in data.get("data", []) if int(pos["netqty"]) != 0
        ]
    
    async def get_ltp(self, symbol: str) -> float:
        payload = {
            "mode": "LTP",
            "exchangeTokens": {"NSE": [symbol]}
        }
        response = await self.http_client.post(
            "/rest/secure/angelbroking/market/v1/quote",
            json=payload
        )
        data = response.json()
        return float(data["data"]["fetched"][0]["ltp"])
    
    async def get_order_status(self, order_id: str) -> OrderStatus:
        response = await self.http_client.get(
            "/rest/secure/angelbroking/order/v1/getOrderBook"
        )
        data = response.json()
        for order in data.get("data", []):
            if order["orderid"] == order_id:
                status_map = {
                    "complete": OrderStatus.COMPLETE,
                    "rejected": OrderStatus.REJECTED,
                    "cancelled": OrderStatus.CANCELLED,
                    "open": OrderStatus.OPEN,
                }
                return status_map.get(order["status"].lower(), OrderStatus.PENDING)
        return OrderStatus.PENDING
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-018: Create AES-256 Encryption Utilities

**File**: `backend/app/core/encryption.py`

**Description**: Create encryption utilities for secure storage of broker credentials using AES-256.

**Acceptance Criteria**:
- [ ] `encrypt(plaintext: str) -> str` - encrypts data with AES-256
- [ ] `decrypt(ciphertext: str) -> str` - decrypts data
- [ ] Uses environment variable for encryption key
- [ ] Key must be 32 bytes (256 bits)
- [ ] Uses GCM mode for authenticated encryption
- [ ] Generates unique IV for each encryption

**Code Reference**:
```python
import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings

class EncryptionService:
    """AES-256-GCM encryption for sensitive data"""
    
    def __init__(self):
        # Key must be 32 bytes for AES-256
        key_b64 = settings.ENCRYPTION_KEY
        self.key = base64.b64decode(key_b64)
        if len(self.key) != 32:
            raise ValueError("Encryption key must be 32 bytes (256 bits)")
        self.aesgcm = AESGCM(self.key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext and return base64-encoded ciphertext"""
        # Generate random 12-byte IV
        iv = os.urandom(12)
        # Encrypt
        ciphertext = self.aesgcm.encrypt(iv, plaintext.encode('utf-8'), None)
        # Combine IV + ciphertext and base64 encode
        combined = iv + ciphertext
        return base64.b64encode(combined).decode('utf-8')
    
    def decrypt(self, encrypted: str) -> str:
        """Decrypt base64-encoded ciphertext"""
        combined = base64.b64decode(encrypted)
        # Extract IV (first 12 bytes) and ciphertext
        iv = combined[:12]
        ciphertext = combined[12:]
        # Decrypt
        plaintext = self.aesgcm.decrypt(iv, ciphertext, None)
        return plaintext.decode('utf-8')

# Singleton instance
_encryption_service = None

def get_encryption_service() -> EncryptionService:
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service

def encrypt(plaintext: str) -> str:
    return get_encryption_service().encrypt(plaintext)

def decrypt(ciphertext: str) -> str:
    return get_encryption_service().decrypt(ciphertext)
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-019: Create Broker Connect Endpoint

**File**: `backend/app/api/broker.py`

**Description**: Create `/broker/connect` POST endpoint to validate broker type, encrypt and store credentials.

**Acceptance Criteria**:
- [ ] Accepts broker_type, api_key, api_secret, access_token
- [ ] Validates broker_type is supported (zerodha, dhan, fyers, angel_one)
- [ ] Creates broker instance and validates credentials
- [ ] Encrypts all credentials with AES-256
- [ ] Stores encrypted credentials in database
- [ ] Returns connection status
- [ ] Requires authenticated user

**Code Reference**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.core.database import get_db
from app.services.broker_service import connect_broker

router = APIRouter(prefix="/broker", tags=["Broker"])

class BrokerConnectRequest(BaseModel):
    broker_type: str  # zerodha, dhan, fyers, angel_one
    api_key: str
    api_secret: str
    access_token: str

class BrokerConnectResponse(BaseModel):
    status: str  # connected, failed
    broker_type: str
    message: str

@router.post("/connect", response_model=BrokerConnectResponse)
async def connect_broker_endpoint(
    request: BrokerConnectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Validate broker type
    valid_brokers = ["zerodha", "dhan", "fyers", "angel_one"]
    if request.broker_type not in valid_brokers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid broker type. Must be one of: {valid_brokers}"
        )
    
    result = await connect_broker(
        db=db,
        user_id=current_user.id,
        broker_type=request.broker_type,
        api_key=request.api_key,
        api_secret=request.api_secret,
        access_token=request.access_token
    )
    
    if result.success:
        return BrokerConnectResponse(
            status="connected",
            broker_type=request.broker_type,
            message="Broker connected successfully"
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=result.error_message
        )
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-020: Create Broker Validate Endpoint

**File**: `backend/app/api/broker.py`

**Description**: Add `/broker/validate` POST endpoint to test broker connection without storing credentials.

**Acceptance Criteria**:
- [ ] Accepts same fields as /broker/connect
- [ ] Creates broker instance and tests connection
- [ ] Does NOT store credentials
- [ ] Returns validation result with success/failure
- [ ] Useful for testing before saving

**Code Reference**:
```python
class BrokerValidateRequest(BaseModel):
    broker_type: str
    api_key: str
    api_secret: str
    access_token: str

class BrokerValidateResponse(BaseModel):
    is_valid: bool
    message: str

@router.post("/validate", response_model=BrokerValidateResponse)
async def validate_broker_endpoint(
    request: BrokerValidateRequest,
    current_user: User = Depends(get_current_user)
):
    broker = get_broker_instance(request.broker_type)
    
    try:
        connected = await broker.connect(
            api_key=request.api_key,
            api_secret=request.api_secret,
            access_token=request.access_token
        )
        
        if connected and await broker.validate():
            return BrokerValidateResponse(
                is_valid=True,
                message="Broker credentials are valid"
            )
        else:
            return BrokerValidateResponse(
                is_valid=False,
                message="Broker credentials validation failed"
            )
    except Exception as e:
        return BrokerValidateResponse(
            is_valid=False,
            message=f"Validation error: {str(e)}"
        )
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-021: Create Broker Disconnect Endpoint

**File**: `backend/app/api/broker.py`

**Description**: Add `/broker/disconnect` DELETE endpoint to remove broker connection securely.

**Acceptance Criteria**:
- [ ] Requires authenticated user
- [ ] Deletes broker credentials from database
- [ ] Clears any cached broker connections
- [ ] Returns success message
- [ ] Checks user owns the broker connection

**Code Reference**:
```python
@router.delete("/disconnect")
async def disconnect_broker_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Find user's broker credential
    result = await db.execute(
        select(BrokerCredential).where(BrokerCredential.user_id == current_user.id)
    )
    broker_cred = result.scalar_one_or_none()
    
    if not broker_cred:
        raise HTTPException(status_code=404, detail="No broker connection found")
    
    # Delete from database
    await db.delete(broker_cred)
    await db.commit()
    
    # Clear from cache if exists
    await clear_broker_cache(current_user.id)
    
    return {"message": "Broker disconnected successfully"}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-022: Create Broker Status Endpoint

**File**: `backend/app/api/broker.py`

**Description**: Add `/broker/status` GET endpoint to check current broker connection health.

**Acceptance Criteria**:
- [ ] Returns broker type and connection status
- [ ] Validates current credentials still work
- [ ] Returns token expiry warning if applicable
- [ ] Returns 404 if no broker connected
- [ ] Caches health check result for 1 minute

**Code Reference**:
```python
class BrokerStatusResponse(BaseModel):
    is_connected: bool
    broker_type: str
    status: str  # healthy, token_expired, error
    message: str
    connected_at: datetime

@router.get("/status", response_model=BrokerStatusResponse)
async def get_broker_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get user's broker credential
    result = await db.execute(
        select(BrokerCredential).where(BrokerCredential.user_id == current_user.id)
    )
    broker_cred = result.scalar_one_or_none()
    
    if not broker_cred:
        raise HTTPException(status_code=404, detail="No broker connection found")
    
    # Check if cached status exists
    cached = await get_cached_broker_status(current_user.id)
    if cached:
        return cached
    
    # Validate connection
    broker = await get_broker_for_user(current_user.id, db)
    is_valid = await broker.validate()
    
    status_response = BrokerStatusResponse(
        is_connected=is_valid,
        broker_type=broker_cred.broker_type,
        status="healthy" if is_valid else "error",
        message="Connection is active" if is_valid else "Connection validation failed",
        connected_at=broker_cred.created_at
    )
    
    # Cache for 1 minute
    await cache_broker_status(current_user.id, status_response, ttl=60)
    
    return status_response
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-023: Create BrokerCredential Model

**File**: `backend/app/models/broker.py`

**Description**: Create BrokerCredential SQLAlchemy model for storing encrypted broker credentials.

**Acceptance Criteria**:
- [ ] `id` - String primary key with `brk_` prefix
- [ ] `user_id` - Foreign key to users table
- [ ] `broker_type` - String (zerodha, dhan, fyers, angel_one)
- [ ] `encrypted_api_key` - Text, encrypted
- [ ] `encrypted_secret` - Text, encrypted
- [ ] `encrypted_token` - Text, encrypted
- [ ] `is_valid` - Boolean, default True
- [ ] `created_at` - DateTime
- [ ] `updated_at` - DateTime
- [ ] Unique constraint on user_id (one broker per user for MVP)

**Code Reference**:
```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

def generate_broker_id() -> str:
    return f"brk_{uuid.uuid4().hex[:12]}"

class BrokerCredential(Base):
    __tablename__ = "broker_credentials"
    
    id = Column(String(50), primary_key=True, default=generate_broker_id)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, unique=True)
    broker_type = Column(String(50), nullable=False)  # zerodha, dhan, fyers, angel_one
    encrypted_api_key = Column(Text, nullable=False)
    encrypted_secret = Column(Text, nullable=False)
    encrypted_token = Column(Text, nullable=False)
    is_valid = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    # user = relationship("User", back_populates="broker_credential")
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-024: Create Broker Service

**File**: `backend/app/services/broker_service.py`

**Description**: Create broker service with `connect_broker()`, `validate_broker()`, `get_broker_instance()` functions.

**Acceptance Criteria**:
- [ ] `connect_broker(db, user_id, broker_type, ...)` - connects and stores
- [ ] `validate_broker(db, user_id)` - validates stored credentials
- [ ] `get_broker_instance(broker_type)` - factory function
- [ ] `get_broker_for_user(user_id, db)` - returns connected broker for user
- [ ] Decrypts credentials when needed
- [ ] Proper error handling

**Code Reference**:
```python
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.broker import BrokerCredential
from app.core.encryption import encrypt, decrypt
from app.brokers.base import BaseBroker
from app.brokers.zerodha import ZerodhaBroker
from app.brokers.dhan import DhanBroker
from app.brokers.fyers import FyersBroker
from app.brokers.angel_one import AngelOneBroker

@dataclass
class ConnectResult:
    success: bool
    error_message: str = ""

def get_broker_instance(broker_type: str) -> BaseBroker:
    """Factory function to create broker instance"""
    brokers = {
        "zerodha": ZerodhaBroker,
        "dhan": DhanBroker,
        "fyers": FyersBroker,
        "angel_one": AngelOneBroker,
    }
    broker_class = brokers.get(broker_type)
    if not broker_class:
        raise ValueError(f"Unknown broker type: {broker_type}")
    return broker_class()

async def connect_broker(
    db: AsyncSession,
    user_id: str,
    broker_type: str,
    api_key: str,
    api_secret: str,
    access_token: str
) -> ConnectResult:
    """Connect to broker and store encrypted credentials"""
    
    # Get broker instance and validate
    broker = get_broker_instance(broker_type)
    
    try:
        connected = await broker.connect(api_key, api_secret, access_token)
        if not connected:
            return ConnectResult(success=False, error_message="Failed to connect to broker")
        
        is_valid = await broker.validate()
        if not is_valid:
            return ConnectResult(success=False, error_message="Broker credential validation failed")
    except Exception as e:
        return ConnectResult(success=False, error_message=str(e))
    
    # Delete existing credential if any
    result = await db.execute(
        select(BrokerCredential).where(BrokerCredential.user_id == user_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
    
    # Create new credential with encrypted values
    credential = BrokerCredential(
        user_id=user_id,
        broker_type=broker_type,
        encrypted_api_key=encrypt(api_key),
        encrypted_secret=encrypt(api_secret),
        encrypted_token=encrypt(access_token),
        is_valid=True
    )
    db.add(credential)
    await db.commit()
    
    return ConnectResult(success=True)

async def get_broker_for_user(user_id: str, db: AsyncSession) -> BaseBroker:
    """Get connected broker instance for user"""
    result = await db.execute(
        select(BrokerCredential).where(BrokerCredential.user_id == user_id)
    )
    cred = result.scalar_one_or_none()
    
    if not cred:
        raise ValueError("No broker connected for user")
    
    broker = get_broker_instance(cred.broker_type)
    await broker.connect(
        api_key=decrypt(cred.encrypted_api_key),
        api_secret=decrypt(cred.encrypted_secret),
        access_token=decrypt(cred.encrypted_token)
    )
    
    return broker
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-025: Implement Broker Factory Pattern

**File**: `backend/app/brokers/__init__.py`

**Description**: Implement broker factory pattern to instantiate correct broker based on type.

**Acceptance Criteria**:
- [ ] Exports all broker classes
- [ ] `create_broker(broker_type: str) -> BaseBroker`
- [ ] `SUPPORTED_BROKERS` list for validation
- [ ] Type hints for all exports

**Code Reference**:
```python
from typing import Type, Dict, List
from app.brokers.base import BaseBroker
from app.brokers.zerodha import ZerodhaBroker
from app.brokers.dhan import DhanBroker
from app.brokers.fyers import FyersBroker
from app.brokers.angel_one import AngelOneBroker

# Registry of supported brokers
BROKER_REGISTRY: Dict[str, Type[BaseBroker]] = {
    "zerodha": ZerodhaBroker,
    "dhan": DhanBroker,
    "fyers": FyersBroker,
    "angel_one": AngelOneBroker,
}

SUPPORTED_BROKERS: List[str] = list(BROKER_REGISTRY.keys())

def create_broker(broker_type: str) -> BaseBroker:
    """Factory function to create broker instance by type"""
    broker_class = BROKER_REGISTRY.get(broker_type.lower())
    if not broker_class:
        raise ValueError(
            f"Unsupported broker type: {broker_type}. "
            f"Supported brokers: {SUPPORTED_BROKERS}"
        )
    return broker_class()

def is_supported_broker(broker_type: str) -> bool:
    """Check if broker type is supported"""
    return broker_type.lower() in BROKER_REGISTRY

__all__ = [
    "BaseBroker",
    "ZerodhaBroker",
    "DhanBroker",
    "FyersBroker",
    "AngelOneBroker",
    "create_broker",
    "is_supported_broker",
    "SUPPORTED_BROKERS",
]
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-026: Add Token Expiry Notification System

**File**: `backend/app/services/broker_service.py`

**Description**: Add access token expiry notification system to check token validity and alert user.

**Acceptance Criteria**:
- [ ] Check token validity on each broker operation
- [ ] Mark credential as invalid if token expired
- [ ] Create notification for user about expired token
- [ ] Add endpoint to refresh/update token
- [ ] Background job to check token validity daily

**Code Reference**:
```python
from app.services.notification_service import send_notification

async def check_token_validity(user_id: str, db: AsyncSession) -> bool:
    """Check if user's broker token is still valid"""
    result = await db.execute(
        select(BrokerCredential).where(BrokerCredential.user_id == user_id)
    )
    cred = result.scalar_one_or_none()
    
    if not cred:
        return False
    
    broker = get_broker_instance(cred.broker_type)
    try:
        await broker.connect(
            api_key=decrypt(cred.encrypted_api_key),
            api_secret=decrypt(cred.encrypted_secret),
            access_token=decrypt(cred.encrypted_token)
        )
        is_valid = await broker.validate()
        
        if not is_valid and cred.is_valid:
            # Token just expired, notify user
            cred.is_valid = False
            await db.commit()
            
            await send_notification(
                user_id=user_id,
                notification_type="token_expiry",
                title="Broker Token Expired",
                message=f"Your {cred.broker_type} access token has expired. Please reconnect your broker."
            )
        
        return is_valid
    except Exception:
        return False

async def update_broker_token(
    user_id: str,
    new_access_token: str,
    db: AsyncSession
) -> bool:
    """Update broker access token"""
    result = await db.execute(
        select(BrokerCredential).where(BrokerCredential.user_id == user_id)
    )
    cred = result.scalar_one_or_none()
    
    if not cred:
        return False
    
    # Validate new token
    broker = get_broker_instance(cred.broker_type)
    await broker.connect(
        api_key=decrypt(cred.encrypted_api_key),
        api_secret=decrypt(cred.encrypted_secret),
        access_token=new_access_token
    )
    
    if await broker.validate():
        cred.encrypted_token = encrypt(new_access_token)
        cred.is_valid = True
        cred.updated_at = func.now()
        await db.commit()
        return True
    
    return False
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-027: Write Broker Integration Tests

**File**: `backend/tests/test_broker.py`

**Description**: Write integration tests with mocked broker API responses.

**Acceptance Criteria**:
- [ ] Test broker connection with valid credentials
- [ ] Test broker connection with invalid credentials
- [ ] Test credential encryption/decryption
- [ ] Test broker disconnect
- [ ] Test broker status endpoint
- [ ] Test broker factory pattern
- [ ] Mock all external broker API calls
- [ ] Test each broker implementation

**Code Reference**:
```python
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from app.main import app
from app.brokers import create_broker, SUPPORTED_BROKERS
from app.core.encryption import encrypt, decrypt

@pytest.mark.asyncio
async def test_encryption_roundtrip():
    """Test encryption and decryption work correctly"""
    original = "super-secret-api-key"
    encrypted = encrypt(original)
    decrypted = decrypt(encrypted)
    assert decrypted == original
    assert encrypted != original

@pytest.mark.asyncio
async def test_broker_factory():
    """Test broker factory creates correct instances"""
    for broker_type in SUPPORTED_BROKERS:
        broker = create_broker(broker_type)
        assert broker is not None
        assert broker.BROKER_TYPE == broker_type

@pytest.mark.asyncio
async def test_broker_factory_invalid_type():
    """Test broker factory raises error for invalid type"""
    with pytest.raises(ValueError):
        create_broker("invalid_broker")

@pytest.mark.asyncio
@patch("app.brokers.zerodha.ZerodhaBroker.connect")
@patch("app.brokers.zerodha.ZerodhaBroker.validate")
async def test_connect_broker_success(mock_validate, mock_connect, auth_headers):
    """Test successful broker connection"""
    mock_connect.return_value = True
    mock_validate.return_value = True
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/broker/connect",
            headers=auth_headers,
            json={
                "broker_type": "zerodha",
                "api_key": "test_key",
                "api_secret": "test_secret",
                "access_token": "test_token"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "connected"

@pytest.mark.asyncio
@patch("app.brokers.zerodha.ZerodhaBroker.connect")
async def test_connect_broker_invalid_credentials(mock_connect, auth_headers):
    """Test broker connection with invalid credentials"""
    mock_connect.return_value = False
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/broker/connect",
            headers=auth_headers,
            json={
                "broker_type": "zerodha",
                "api_key": "invalid_key",
                "api_secret": "invalid_secret",
                "access_token": "invalid_token"
            }
        )
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_broker_status_no_connection(auth_headers):
    """Test broker status when no broker connected"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/broker/status", headers=auth_headers)
        assert response.status_code == 404
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/brokers/base.py` | Create | Abstract broker interface |
| `backend/app/brokers/zerodha.py` | Create | Zerodha implementation |
| `backend/app/brokers/dhan.py` | Create | Dhan implementation |
| `backend/app/brokers/fyers.py` | Create | Fyers implementation |
| `backend/app/brokers/angel_one.py` | Create | Angel One implementation |
| `backend/app/brokers/__init__.py` | Modify | Broker factory pattern |
| `backend/app/core/encryption.py` | Create | AES-256 encryption |
| `backend/app/api/broker.py` | Modify | Broker endpoints |
| `backend/app/models/broker.py` | Modify | BrokerCredential model |
| `backend/app/services/broker_service.py` | Create | Broker service |
| `backend/tests/test_broker.py` | Create | Broker tests |

---

## Environment Variables Required

```bash
# Encryption Key (32 bytes, base64 encoded)
ENCRYPTION_KEY="your-32-byte-key-base64-encoded=="
```

---

## Definition of Done

- [ ] All 15 tasks completed
- [ ] All broker implementations tested
- [ ] Encryption working correctly
- [ ] Integration tests passing
- [ ] Code reviewed and approved
- [ ] API documentation updated

---

## Next Phase

After completing Phase 2, proceed to [Phase 3: Strategy Management Module](./phase-03-strategy-management.md)
