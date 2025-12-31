"""
Validators for Binance trading bot with logging
"""

from typing import Optional
from binance.client import Client
from src.utils.logging import get_logger

logger = get_logger()

class Validator:
    """
    All the validators are defined under this validator class
    """
    @staticmethod
    def validate_api_keys(api_key: Optional[str], secret_key: Optional[str]) -> None:
        """
        Check if api key and secret key exist or not
        """
        if not api_key or not secret_key:
            logger.error("API key or Secret key is missing or invalid")
            raise ValueError("API key or Secret key is missing or invalid")
        logger.debug("API keys validated successfully")

    @staticmethod
    def validate_testnet(testnet: Optional[bool]) -> bool:
        """
        Check if testnet is True or not
        """
        if testnet is None:
            testnet = True
        if not isinstance(testnet, bool):
            logger.error("Testnet flag must be a boolean")
            raise ValueError("Testnet flag must be a boolean")
        logger.debug(f"Testnet flag validated: {testnet}")
        return testnet

    @staticmethod
    def validate_order_params(symbol: str, quantity: float, price: Optional[float] = None) -> None:
        """
        Check all the parameters before placing the orders
        """
        if not symbol or not isinstance(symbol, str):
            logger.error("Symbol must be a valid string")
            raise ValueError("Symbol must be a valid string")
        if quantity <= 0:
            logger.error("Quantity must be a positive number")
            raise ValueError("Quantity must be a positive number")
        if price is not None and price <= 0:
            logger.error("Price must be positive if provided")
            raise ValueError("Price must be positive if provided")
        logger.debug(
            f"Order parameters validated: symbol={symbol}, quantity={quantity}, price={price}"
        )

    @staticmethod
    def validate_symbol(symbol: str, client: Client) -> None:
        """
        Checks if the given symbol exists on Binance futures.
        """
        try:
            exchange_info = client.futures_exchange_info()
            valid_symbols = [item['symbol'] for item in exchange_info['symbols']]
            if symbol not in valid_symbols:
                logger.error(f"Symbol '{symbol}' is not available on Binance Futures")
                raise ValueError(f"Symbol '{symbol}' is not available on Binance Futures")
            logger.debug(f"Symbol '{symbol}' is valid on Binance Futures")
        except Exception as e:
            logger.error(f"Error fetching exchange info: {e}")
            raise

    @staticmethod
    def validate_side(side: str) -> None:
        """Ensure order side is BUY or SELL"""
        if side.upper() not in ["BUY", "SELL"]:
            logger.error("Side must be BUY or SELL")
            raise ValueError("Side must be BUY or SELL")
        logger.debug(f"Side validated: {side}")

    @staticmethod
    def validate_quantity_price(symbol: str, quantity: float, price: float, client: Client) -> None:
        """
        Ensure quantity and price are positive numbers and above Binance minimums.

        :param symbol: Trading pair
        :param quantity: Amount to trade
        :param price: Order price
        :param client: Binance client
        """
        if quantity <= 0:
            logger.error("Quantity must be greater than zero")
            raise ValueError("Quantity must be greater than zero")
        if price <= 0:
            logger.error("Price must be greater than zero")
            raise ValueError("Price must be greater than zero")

        try:
            exchange_info = client.futures_exchange_info()
            symbol_info = next(
                item for item in exchange_info['symbols'] if item['symbol'] == symbol
            )
            min_price = float(symbol_info['filters'][0]['minPrice'])
            if price < min_price:
                logger.error(f"Price {price} is less than min price {min_price} for {symbol}")
            logger.debug(
                f"Quantity and price validated: quantity={quantity}, price={price} (min {min_price})"
            )
        except StopIteration:
            logger.error(f"Symbol info not found for {symbol}")

    @staticmethod
    def validate_time_in_force(tif: str) -> None:
        """Ensure timeInForce is valid"""
        valid_tif = ["GTC", "IOC", "FOK"]
        if tif.upper() not in valid_tif:
            logger.error(f"Invalid timeInForce '{tif}'. Must be one of {valid_tif}")
        logger.debug(f"timeInForce validated: {tif}")

    @staticmethod
    def validate_min_notional(
        symbol: str,
        quantity: float,
        client: Client,
        min_notional_usd: float = 100
        ) -> None:
        """
        Ensure the order meets the minimum notional value on Binance Futures.

        :param symbol: Trading pair
        :param quantity: Amount of asset to buy/sell
        :param client: Binance client
        :param min_notional_usd: Minimum USD value (default $100)
        """
        try:
            price = float(client.futures_symbol_ticker(symbol=symbol)["price"])
            notional = quantity * price
            if notional < min_notional_usd:
                logger.error(
                    f"Order value for {symbol} is too small: {notional:.2f} USD. Minimum is {min_notional_usd} USD"
                )
                raise ValueError(f"Minimum order value for {symbol} is {min_notional_usd} USD")
            logger.debug(f"Notional value validated: {notional:.2f} USD for symbol {symbol}")
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}", exc_info=True)
            raise

    @staticmethod
    def validate_quantity_bounds(
        symbol: str,
        quantity: float,
        client: Client,
        leverage: int = 20,
        min_usd: float = 100
        ) -> float:
        """
        Validate and auto-adjust quantity based on:
        - Binance minimum notional (~$100)
        - Available margin with given leverage
        Returns a safe quantity that can be placed.
        """
        price = float(client.futures_symbol_ticker(symbol=symbol)["price"])

        min_qty = round(min_usd / price, 6)

        bal = float(next(
            b["balance"] for b in client.futures_account_balance() if b["asset"] == "USDT"
        ))
        max_qty = round((bal * leverage * 0.8) / price, 6)
        if quantity < min_qty:
            logger.warning(f"Quantity {quantity} too low, adjusted → {min_qty}")
            return min_qty

        if quantity > max_qty:
            logger.warning(f"Quantity {quantity} too high, adjusted → {max_qty}")
            return max_qty

        return quantity

    @staticmethod
    def validate_leverage(leverage: int) -> int:
        """Ensure leverage is within Binance Futures safe range."""
        if not isinstance(leverage, int):
            raise ValueError("Leverage must be an integer")
        if leverage < 1 or leverage > 125:
            raise ValueError("Leverage must be between 1 and 125")
        logger.debug(f"Leverage validated: {leverage}")
        return leverage
    
    @staticmethod
    def validate_margin(client: Client, min_usd_required: float = 10) -> float:
        """
        Ensure the account has minimum USDT balance to trade.
        """
        bal = float(next(
            b["balance"] for b in client.futures_account_balance() if b["asset"] == "USDT"
        ))
        if bal < min_usd_required:
            raise ValueError(
                f"Insufficient balance: {bal} USDT. Minimum required is {min_usd_required} USDT"
                )
        logger.debug(f"Available USDT balance validated: {bal}")
        return bal

    @staticmethod
    def validate_market_status(client: Client) -> None:
        """Check if Binance Futures system is online."""
        status = client.futures_ping()
        if status is None:
            logger.error("Binance Futures API is unreachable")
            raise ConnectionError("Binance Futures API is unreachable")
        logger.debug("Binance Futures API is online and reachable")
