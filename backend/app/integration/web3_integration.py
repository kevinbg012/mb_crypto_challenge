from app.core.config import settings
from web3.types import Wei, TxReceipt

web3 = settings.WEB3_PROVIDER

def get_transaction(tx_hash: str):
    try:
        return web3.eth.get_transaction(tx_hash)
    except Exception as e:
        print(f"Error retrieving transaction: {e}")
        raise e

def get_transaction_receipt(tx_hash: str) -> TxReceipt | None:
    try:
        return web3.eth.get_transaction_receipt(tx_hash)
    except Exception as e:
        print(f"Error retrieving transaction receipt: {e}")
        raise e

def confirmations(tx_hash):
  tx = web3.eth.get_transaction(tx_hash)
  return web3.eth.block_number - tx.blockNumber

def is_transaction_confirmed(tx_hash, confirmations_required=6) -> bool:
    try:
        tx_receipt = get_transaction_receipt(tx_hash)
        return tx_receipt.get("status") == 1 and confirmations(tx_hash) >= confirmations_required
    except Exception as e:
        print(f"Error checking transaction: {e}")
        return False

def is_transaction_failed(tx_hash: str) -> bool:
    try:
        tx_receipt = get_transaction_receipt(tx_hash)
        return tx_receipt.get("status") == 0
    except:
        try:
            tx = get_transaction(tx_hash)
            return tx is None
        except:
            return False

def send_transaction(transaction):
    try:
        tx_hash = web3.eth.send_transaction(transaction)
        return tx_hash
    except Exception as e:
        print(f"Error sending transaction: {e}")
        return None

def get_gas_price():
    try:
        return web3.eth.gas_price
    except Exception as e:
        print(f"Error retrieving gas price: {e}")
        return None

def is_contract_transaction(tx_hash: str) -> bool:
    try:
        tx = web3.eth.get_transaction(tx_hash)

        code_at_to = web3.eth.get_code(tx['to'])
        is_contract = len(code_at_to) > 0

        is_function_call = tx['input'] != '0x'

        return is_contract and is_function_call
    except Exception as e:
        print(f"Error checking if transaction is a contract interaction: {e}")
        return False

def get_address_nonce(address: str) -> int:
    try:
        return web3.eth.get_transaction_count(address)
    except Exception as e:
        print(f"Error retrieving nonce for address {address}: {e}")
        raise e

def sign_and_send_transaction(transaction, private_key: str) -> str:
    try:
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx["raw_transaction"])
        return web3.to_hex(tx_hash)
    except Exception as e:
        print(f"Error signing and sending transaction: {e}")
        raise e

def get_eth_balance(address: str) -> Wei:
    try:
        return web3.eth.get_balance(address)
    except Exception as e:
        print(f"Error retrieving ETH balance for address {address}: {e}")
        return Wei(0)

def get_transaction_estimate(transaction) -> int:
    try:
        return web3.eth.estimate_gas(transaction)
    except Exception as e:
        print(f"Error estimating gas for transaction: {e}")
        return 0