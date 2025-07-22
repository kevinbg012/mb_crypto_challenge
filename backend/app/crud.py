import uuid
from typing import Any

from sqlmodel import Session, select

from app.models import *


from app.models import AddressCreationJob, Address, TransactionHistory, Transaction
from app.api.models.models import AddressCreationStatus
from app.utils import get_random_eth_address

from app.api.models.models import CreateAddressJobRequest

from web3.types import TxData, TxReceipt
from web3 import Web3

from decimal import Decimal

def create_address_job(*, session: Session, job_data: CreateAddressJobRequest) -> Any:
    job = AddressCreationJob(quantity = job_data.quantity)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job

def get_create_address_jobs(*, session: Session) -> AddressCreationJob:
    print("getting inside get_create_address_jobs")
    statement = select(AddressCreationJob).where(AddressCreationJob.status == AddressCreationStatus.PENDING).order_by(AddressCreationJob.created_at)
    job = session.exec(statement).first()
    return job

def create_addresses(*, session: Session, quantity: int):
    addresses = []
    for _ in range(quantity):
        addresses.append(get_random_eth_address())
    session.add_all(addresses)

def get_addresses(*, session: Session) -> list[Address]:
    statement = select(Address) #.offset(skip).limit(limit)
    addresses = session.exec(statement).all()
    return addresses

def check_address_exists(*, session: Session, address: str) -> bool:
    statement = select(Address).where(Address.address == address)
    existing_address = session.exec(statement).first()
    return existing_address is not None

def get_address(*, session: Session, address: str) -> Address:
    statement = select(Address).where(Address.address == address)
    existing_address = session.exec(statement).first()
    return existing_address

def create_transaction_history_from_eth_tx(*, session: Session, transactions_hash: str, transaction_data: TxData, transaction_receipt: TxReceipt) -> TransactionHistory:
    amount = Web3.from_wei(int(transaction_data['value']), 'ether')  # Convert wei to ether
    transaction_history = TransactionHistory(transaction_hash=transactions_hash,from_address=transaction_data['from'],
                                             to_address=transaction_data['to'], asset='ETH',
                                             amount=amount, gas=transaction_receipt['gasUsed'],
                                             gas_price=transaction_receipt['effectiveGasPrice'], block_number=transaction_data['blockNumber'])

    session.add(transaction_history)
    session.commit()
    session.refresh(transaction_history)
    return transaction_history

def create_transaction_history_from_contract_tx(*, session: Session, transactions_hash: str, transaction_data: TxReceipt, address: str, amount: Decimal, asset: str) -> TransactionHistory:
    transaction_history = TransactionHistory(transaction_hash=transactions_hash,from_address=transaction_data['from'],
                                             to_address=address, asset=asset,
                                             amount=amount, gas=transaction_data['gasUsed'],
                                             gas_price=transaction_data['effectiveGasPrice'], block_number=transaction_data['blockNumber'])

    session.add(transaction_history)
    session.commit()
    session.refresh(transaction_history)
    return transaction_history

def create_transaction_history_from_tx(*, session: Session, tx: Transaction, tx_receipt: TxReceipt) -> TransactionHistory:
    transaction_history = TransactionHistory(transaction_hash=tx.transaction_hash, from_address=tx.from_address,
                                             to_address=tx.to_address, asset=tx.asset,
                                             amount=tx.amount, gas=  tx_receipt['gasUsed'],
                                             gas_price=tx_receipt['effectiveGasPrice'],
                                             block_number=tx_receipt['blockNumber'])

    session.add(transaction_history)
    session.commit()
    session.refresh(transaction_history)
    return transaction_history

def get_transaction_history_by_address(*, session: Session, address: str) -> list[TransactionHistory]:
    statement = (select(TransactionHistory)
                 .where(TransactionHistory.from_address == address or TransactionHistory.to_address == address)
                 .order_by(TransactionHistory.created_at))
    history = session.exec(statement).all()
    return history

def create_transaction(*, session: Session, transaction_data: Transaction) -> Transaction:
    transaction = Transaction.model_validate(transaction_data)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

def get_transactions_by_status(*, session: Session, status: TransactionStatus) -> list[Transaction]:
    statement = select(Transaction).where(Transaction.status == status).order_by(Transaction.created_at)
    transactions = session.exec(statement).all()
    return transactions

def check_transaction_history_exists(*, session: Session, transaction_hash: str) -> bool:
    statement = select(TransactionHistory).where(TransactionHistory.transaction_hash == transaction_hash)
    existing_transaction = session.exec(statement).first()
    return existing_transaction is not None