import uuid
from datetime import datetime

from enum import Enum
from typing import TypeVar, Generic, Optional

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from decimal import Decimal

T = TypeVar("T")

class ResponseModel(GenericModel, Generic[T]):
    status: str
    message: Optional[str]
    data: Optional[T]

class AddressCreationStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    STARTED = "started"
    CONFIRMED = "confirmed"
    FAILED = "failed"

# address creation endpoints
class CreateAddressJobRequest(BaseModel):
    quantity: int

class CreateAddressResponse(BaseModel):
    job_id: uuid.UUID
    quantity: int
    status: AddressCreationStatus

class AddressResponse(BaseModel):
    id: uuid.UUID
    address: str
    created_at: datetime

class AddressesResponse(BaseModel):
    data: list[AddressResponse]
    count: int

# transaction related endpoints
class CreateTransactionRequest(BaseModel):
    from_address: str = Field(
        ...,
        description="Endereço de origem do saldo a ser transferido",
        max_length=42
    )
    to_address: str = Field(
        ...,
        description="Endereço de destino da transferência",
        max_length=42
    )
    asset: str = Field(
        ...,
        description="Ativo a ser transferido (ex: ETH, USDC, USDT, ...)",
        max_length=20
    )
    amount: Decimal = Field(
        ...,
        description="Valor da transferência (formato Decimal)",
        ge=0
    )

class TransactionHistoryResponse(BaseModel):
    transaction_hash: str
    from_address: str
    to_address: str
    asset: str
    amount: Decimal
    gas: int
    gas_price: Decimal
    block_number: int
    created_at: datetime

class TransactionResponse(BaseModel):
    transaction_hash: Optional[str]
    from_address: str
    to_address: str
    asset: str
    amount: Decimal
    status: TransactionStatus
    created_at: datetime

class ValidateTransactionRequest(BaseModel):
    transaction_hash: str = Field(
        ...,
        description="Hash da transação a ser validada",
        max_length=100
    )