import uuid
from datetime import datetime
from decimal import Decimal
from sqlmodel import Field, SQLModel, Column, DateTime, func, BigInteger
from typing import Optional

from app.api.models.models import AddressCreationStatus, TransactionStatus

class AddressCreationJob(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    quantity: int = Field(default=1, ge=1, le=1000)
    status: AddressCreationStatus = Field(default=AddressCreationStatus.PENDING, max_length=20)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

class Address(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    address: str = Field(unique=True, index=True, max_length=42)
    index: int = Field(..., sa_column=Column(BigInteger), ge=0, le=2**32 - 1, description="Index of the address in the wallet")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

class Transaction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
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
    transaction_hash: Optional[str] = Field(default=None, unique=True, index=True, max_length=66)
    block_number: Optional[int] = Field(default=None, ge=0, description="Block number in which the transaction was included")
    created_at: Optional[datetime] = Field(default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
    status: TransactionStatus = Field(default=TransactionStatus.PENDING, max_length=20, description="Status of the transaction (pending, confirmed, failed)")

class TransactionHistory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    transaction_hash: str = Field(unique=True, index=True, max_length=66)
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
    gas: int
    gas_price: int = Field(
        ...,
        description="Preço do gás em wei (formato Decimal)",
        ge=0
    )
    block_number: int = Field(
        ...,
        description="Número do bloco em que a transação foi incluída",
        ge=0
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )