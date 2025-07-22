from contextlib import contextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session

from app import crud
from app.api.models.models import AddressCreationStatus, TransactionStatus
from app.core.db import engine
from app.utils import get_private_key_from_index

from app.core.config import settings
from app.integration import web3_integration

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def get_db_session():
    with Session(engine) as session:
        yield session

def create_address_job():
    with get_db_session() as session:
        job = crud.get_create_address_jobs(session=session)
        if job:
            crud.create_addresses(session=session, quantity=job.quantity)
            job.status = AddressCreationStatus.COMPLETED
            session.add(job)
            session.commit()

def check_pending_transaction():
    with get_db_session() as session:
        transactions = crud.get_transactions_by_status(session=session, status=TransactionStatus.PENDING)
        for t in transactions:

            token = settings.token_by_symbol.get(t.asset)
            token_contract = token.get("contract")
            decimals = token.get("decimals")
            value = int(t.amount * (10 ** decimals))

            balance = web3_integration.get_eth_balance(t.from_address)
            nonce = web3_integration.get_address_nonce(t.from_address)

            new_tx = token_contract.functions.transfer(t.to_address, value).build_transaction({
                'from': t.from_address,
                'nonce': nonce,
                'chainId': int(settings.CHAIN_ID),
                "gas": 65000,  # Default gas for most ERC20 transfers
                "gasPrice": web3_integration.get_gas_price(),
            })

            estimated_gas = web3_integration.get_transaction_estimate(new_tx)
            if estimated_gas == 0:
                estimated_gas = 65000  # Default gas for most ERC20 transfers
            gas_with_buffer = int(estimated_gas * 1.2)

            gas_price = web3_integration.get_gas_price()

            new_tx["gas"] = gas_with_buffer
            new_tx["gasPrice"] = gas_price

            cost = gas_with_buffer * gas_price

            logger.info("Transaction cost: %s, Balance: %s from wallet %s", cost, balance, t.from_address)
            if cost > balance:
                raise ValueError(
                    "Insufficient funds for transaction. Please ensure you have enough ETH to cover the transfer and gas fees.")

            address = crud.get_address(session=session, address=t.from_address)

            pk = get_private_key_from_index(address.index)
            new_tx_hash = web3_integration.sign_and_send_transaction(transaction=new_tx, private_key=pk)

            t.transaction_hash = new_tx_hash
            t.status = TransactionStatus.STARTED

            session.add(t)
        session.commit()

def check_transaction_finalization():
    with get_db_session() as session:
        transactions = crud.get_transactions_by_status(session=session, status=TransactionStatus.STARTED)
        for t in transactions:
            if web3_integration.is_transaction_confirmed(tx_hash=t.transaction_hash):
                tx_receipt = web3_integration.get_transaction_receipt(tx_hash=t.transaction_hash)
                t.status = TransactionStatus.CONFIRMED
                t.block_number = tx_receipt['blockNumber']
                session.add(t)

                tx_receipt = web3_integration.get_transaction_receipt(tx_hash=t.transaction_hash)
                crud.create_transaction_history_from_tx(session=session, tx=t, tx_receipt=tx_receipt)

            elif web3_integration.is_transaction_failed(tx_hash=t.transaction_hash):
                t.status = TransactionStatus.FAILED
                session.add(t)
        session.commit()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(create_address_job, 'interval', seconds=30, id='create_address_job', replace_existing=True)
    scheduler.add_job(check_pending_transaction, 'interval', seconds=30, id='transaction_job', replace_existing=True)
    scheduler.add_job(check_transaction_finalization, 'interval', seconds=30, id='transaction_finalization_job', replace_existing=True)
    scheduler.start()
    return scheduler