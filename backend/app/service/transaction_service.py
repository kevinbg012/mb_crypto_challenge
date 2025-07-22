import logging

from app.service import address_service
from sqlmodel import Session

from app.core.config import settings

from app.integration import web3_integration
from app import crud

from app.api.models.models import CreateTransactionRequest, TransactionStatus
from app.models import Transaction
from app.utils import get_private_key_from_index, get_main_address, get_private_key_from_master

from decimal import Decimal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

web3 = settings.WEB3_PROVIDER

def get_transactions_history_by_address(session: Session, address: str):
    if not address_service.check_address_exists(session=session, address=address):
        raise ValueError("Address does not exist in the database.")

    return crud.get_transaction_history_by_address(session=session, address=address)

def validate_transaction_hash(session: Session, transaction_hash: str):
    valid = web3_integration.is_transaction_confirmed(tx_hash=transaction_hash)
    if valid:

        if check_transaction_history_exists(session=session, transaction_hash=transaction_hash):
            logger.error("Transaction already exists in the database.")
            raise Exception

        tx = web3_integration.get_transaction(transaction_hash)
        receipt =  web3_integration.get_transaction_receipt(transaction_hash)

        address = tx['to']

        is_contract_transaction = web3_integration.is_contract_transaction(tx_hash=transaction_hash)

        if is_contract_transaction:
            if (token_contract := settings.token_by_contract_address.get(address)) is None:
                logger.error("Token contract not found in settings.")
                raise Exception

            for log in receipt['logs']:
                print("LOG: ", log)
                if log['address'].lower() == token_contract.get("address").lower():
                    # This is a token transfer
                    contract = token_contract.get("contract")
                    event = contract.events.Transfer().process_log(log)
                    asset = token_contract.get("symbol")
                    decimals = token_contract.get("decimals")
                    address = event["args"]["to"]
                    amount = int(event["args"]["value"])

                    quantizer = Decimal("1." + "0" * decimals)
                    amount = Decimal(amount) / Decimal(10 ** decimals)
                    amount.quantize(quantizer)

                    if address_service.check_address_exists(session=session, address=address):
                        crud.create_transaction_history_from_contract_tx(session=session, transactions_hash=transaction_hash, transaction_data=receipt, address=address, amount=amount, asset=asset)
                        return crud.get_transaction_history_by_address(session=session, address=address)
                    else:
                        raise Exception("Address does not exist in the database.")

            raise Exception("Transaction is not a transfer.")

        # is a normal ether transaction
        if address_service.check_address_exists(session=session, address=address):
            crud.create_transaction_history_from_eth_tx(session=session, transactions_hash=transaction_hash, transaction_data=tx, transaction_receipt=receipt)
            return crud.get_transaction_history_by_address(session=session, address=address)
        else:
            raise Exception("Address does not exist in the database.")

    raise Exception("Transaction is not valid.")

def check_transaction_history_exists(session: Session, transaction_hash: str) -> bool:
    return crud.check_transaction_history_exists(session=session, transaction_hash=transaction_hash)

def create_transaction(session: Session, request: CreateTransactionRequest) -> Transaction:

    from_address = request.from_address
    to_address = request.to_address
    asset = request.asset
    amount = request.amount

    if asset == "ETH":
        return create_eth_transaction(session=session, from_address=from_address, to_address=to_address, amount=amount)
    else:
        return create_contract_transaction(session=session, from_address=from_address, to_address=to_address, asset=asset, amount=amount)

def create_eth_transaction(session: Session, from_address: str, to_address: str, amount: Decimal, is_master: bool = False) -> Transaction:
    try:
        address = address_service.get_address(session=session, address=from_address)
    except:
        raise ValueError(f"Address {from_address} does not exist in the database.")

    amount_wei = web3.to_wei(amount, 'ether')
    nonce = web3_integration.get_address_nonce(from_address)

    new_tx = {
        'to': to_address,
        'value': amount_wei,
        'nonce': nonce,
        'chainId': int(settings.CHAIN_ID)
    }

    estimated_gas = web3_integration.get_transaction_estimate(new_tx)
    gas_with_buffer = int(estimated_gas * 1.2)

    gas_price = web3.eth.gas_price
    new_tx["gas"] = gas_with_buffer
    new_tx["gasPrice"] = gas_price

    cost = gas_with_buffer * gas_price

    logger.info("Estimated gas: %s, Gas with buffer: %s, Gas price: %s, Cost: %s", estimated_gas, gas_with_buffer, gas_price, cost)

    eth_fund = web3_integration.get_eth_balance(address.address)

    logger.info("ETH balance for address %s: %s", from_address, eth_fund)
    if cost + amount_wei > eth_fund:
        raise ValueError("Insufficient funds for transaction. Please ensure you have enough ETH to cover the transfer and gas fees.")

    logger.info("signing and sending transaction: %s", new_tx)

    logger.info("Address %s has index %s", from_address, address.index)
    pk = get_private_key_from_master(address.index) if is_master else get_private_key_from_index(address.index)
    new_tx_hash = web3_integration.sign_and_send_transaction(transaction=new_tx, private_key=pk)

    logger.info("Transaction sent with hash: %s", new_tx_hash)

    tx = Transaction(from_address=from_address, to_address=to_address,
                     asset='ETH', amount=amount, transaction_hash=new_tx_hash, status=TransactionStatus.STARTED)
    return crud.create_transaction(session=session, transaction_data=tx)

def create_contract_transaction(session: Session, from_address: str, to_address: str, asset: str, amount: Decimal) -> Transaction:
    token = settings.token_by_symbol.get(asset)
    if token is None:
        raise ValueError(f"Can't create transaction with asset {asset}.")

    token_contract = token.get("contract")
    decimals = token.get("decimals")
    value = int(amount * (10 ** decimals))
    balance_raw = token_contract.functions.balanceOf(from_address).call()

    try:
        address_service.get_address(session=session, address=from_address)
    except:
        raise ValueError(f"Address {from_address} does not exist in the database.")

    if balance_raw < value:
        raise ValueError(
            "Insufficient token balance for transaction. Please ensure you have enough tokens to cover the transfer.")

    nonce = web3_integration.get_address_nonce(from_address)

    new_tx = token_contract.functions.transfer(to_address, value).build_transaction({
        'from': from_address,
        'nonce': nonce,
        'chainId': int(settings.CHAIN_ID)
    })

    estimated_gas = web3_integration.get_transaction_estimate(new_tx)

    # sometimes it start giving errors, with if the contract working fine
    if estimated_gas == 0:
        estimated_gas = 65000 # enough for most ERC20 transfers

    gas_with_buffer = int(estimated_gas * 1.2)

    gas_price = web3.eth.gas_price

    tx = Transaction(from_address=from_address, to_address=to_address,
                     asset=asset, amount=amount, status=TransactionStatus.PENDING)
    main_tx = crud.create_transaction(session=session, transaction_data=tx)

    cost_eth = gas_with_buffer * gas_price
    create_eth_transaction(session=session, from_address=get_main_address(), to_address=from_address, amount=web3.from_wei(cost_eth, 'ether'), is_master=True)

    return main_tx