"""Limit Order Module for Binance Futures Trading Bot"""

from src.utils.logging import configure_logs, get_logger
from src.client import BinanceBot
from src.utils.validators import Validator


configure_logs(verbose=True)
logging = get_logger()

class LimitOrder:
    """Places limit buy/sell orders on Binance Futures Testnet."""

    def __init__(self, bot: BinanceBot) -> None:
        self.bot = bot
        self.client = bot.client

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> dict | None:
        """
        Create a limit order
        
        :param symbol: symbol of order
        :param side: BUY | SELL
        :param quantity: Amount 
        :param price: Price at which you want to order
        :param time_in_force: GTC (default) | IOC | FOK 
        """

        symbol = symbol.upper()
        side = side.upper()
        time_in_force = time_in_force.upper()

        try:
            Validator.validate_symbol(symbol, self.client)
            Validator.validate_side(side)
            Validator.validate_quantity_price(symbol, quantity , price, self.client)
            Validator.validate_time_in_force(time_in_force)
        except ValueError as e:
            logging.warning(f"Order validation failed: {e}")
            return None

        try:
            logging.info(f"Placing Limit Order | {side} | {quantity} | {symbol} | {price} |")
            limit_order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                timeInForce=time_in_force,
                quantity=quantity,
                price=price
            )

            logging.info(f"Limit Order Placed with Order ID {limit_order.get("orderId")}")
            return limit_order

        except Exception as error:
            logging.error(f"Limit order failed: {error}", exc_info=True)
            return None
