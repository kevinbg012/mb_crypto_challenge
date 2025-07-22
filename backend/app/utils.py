import logging
import random
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

from app.models import Address
from app.core.config import settings

web3 = settings.WEB3_PROVIDER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_address_data_by_index_and_mnemonic(mnemonic: str, index: int):
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    return bip44_def_ctx.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(index)

def get_random_eth_address() -> Address:
    index = random.randint(0, 2 ** 32 - 1)
    user_mnemonic = settings.USER_MNEMONIC
    address_data = get_address_data_by_index_and_mnemonic(user_mnemonic, index)
    address = address_data.PublicKey().ToAddress()
    return Address(address=address, index=index)

def get_private_key_from_index(index: int) -> str:
    user_mnemonic = settings.USER_MNEMONIC
    address_data = get_address_data_by_index_and_mnemonic(user_mnemonic, index)
    return address_data.PrivateKey().Raw().ToHex()

def get_main_address() -> str:
    address_data = get_address_data_from_master(0)
    return address_data.PublicKey().ToAddress()

def get_private_key_from_master(index: int) -> str:
    address_data = get_address_data_from_master(index)
    return address_data.PrivateKey().Raw().ToHex()

def get_address_data_from_master(index: int):
    user_mnemonic = settings.MAIN_USER_MNEMONIC
    return get_address_data_by_index_and_mnemonic(user_mnemonic, index)


