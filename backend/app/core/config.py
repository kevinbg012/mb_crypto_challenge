import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

from web3 import Web3
from app.core.abis import ERC20_ABI

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    PROJECT_NAME: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

   # to generate crypto wallets
    USER_MNEMONIC: str
    MAIN_USER_MNEMONIC: str

    # create infura endpoint
    INFURA_ENDPOINT: str
    INFURA_KEY: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def WEB3_PROVIDER(self) -> Web3:
        infura_url = f"{self.INFURA_ENDPOINT}/{self.INFURA_KEY}"
        return Web3(Web3.HTTPProvider(infura_url))

    # contract addresses
    USDC_ADDRESS: str
    PYUSD_ADDRESS: str
    EURC_ADDRESS: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def token_by_symbol(self) -> dict[str, dict[str, Any]]:
        usdc_token_address = Web3.to_checksum_address(self.USDC_ADDRESS)
        usdc_token_contract = self.WEB3_PROVIDER.eth.contract(
            address=usdc_token_address,
            abi=ERC20_ABI,
        )
        pyusd_token_address = Web3.to_checksum_address(self.PYUSD_ADDRESS)
        pyusd_token_contract = self.WEB3_PROVIDER.eth.contract(
            address=pyusd_token_address,
            abi=ERC20_ABI,
        )
        eurc_token_address = Web3.to_checksum_address(self.EURC_ADDRESS)
        eurc_token_contract = self.WEB3_PROVIDER.eth.contract(
            address=eurc_token_address,
            abi=ERC20_ABI,
        )

        return {
            "USDC": {"symbol": "USDC", "address": usdc_token_address, "contract": usdc_token_contract, "decimals": 6},
            "PYUSD": {"symbol": "PYUSD", "address": pyusd_token_address, "contract": pyusd_token_contract, "decimals": 6},
            "EURC": {"symbol": "EURC", "address": eurc_token_address, "contract": eurc_token_contract, "decimals": 6},
        }

    @computed_field  # type: ignore[prop-decorator]
    @property
    def token_by_contract_address(self) -> dict[str, dict[str, Any]]:
        return {
            self.USDC_ADDRESS: self.token_by_symbol.get("USDC"),
            self.PYUSD_ADDRESS: self.token_by_symbol.get("PYUSD"),
            self.EURC_ADDRESS: self.token_by_symbol.get("EURC"),
        }

    CHAIN_ID: str

settings = Settings()  # type: ignore
