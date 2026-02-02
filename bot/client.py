"""
Binance trading bot client is initialized here
"""
import os
from binance.client import Client
from dotenv import load_dotenv
from bot.utils.logging_config import configure_logs, get_logger
from bot.utils.validators import Validator

load_dotenv()
configure_logs(verbose=True)
logger = get_logger()

class BinanceBot:
    """
    Binance future client initializer
    """
    def __init__(self, testnet: bool = True) -> None:

        api_key = os.getenv("API_KEY")
        secret_key = os.getenv("SECRET_KEY")

        #validate api key
        Validator.validate_api_keys(api_key, secret_key)

        #validate testnet flag
        testnet = Validator.validate_testnet(testnet)

        self.client = Client(api_key, secret_key, testnet=testnet)
        self._override_base_urls(testnet)

        logger.info("Binance client initialized successfully")

    def _override_base_urls(self, testnet:bool) -> None:
        if testnet:
            self.client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"
            logger.debug(f"Base Url set to {self.client.FUTURES_URL}")

    def account_info(self):
        """
        fetch user details if client configured successfully
        """
        try:
            account_info = self.client.futures_account()
            logger.info('Client details fetched successfully')
            return account_info
        except Exception as error:
            logger.error(f"Error fetching client details {error}")
            return None

    def check_connection(self) -> bool:
        """This function will check connection"""
        return bool(self.account_info())

    def validate_symbol(self, symbol: str) -> None:
        """
        Validate if the given symbol exists on Binance Futures
        """
        try:
            Validator.validate_symbol(symbol, self.client)
        except ValueError as e:
            logger.warning(f"Symbol validation failed: {e}")
            return None
