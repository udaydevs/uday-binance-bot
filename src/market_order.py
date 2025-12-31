"""Market Order file for Binance Trading Bot"""
from src.client import BinanceBot
from src.utils.logging import configure_logs, get_logger
from src.utils.validators import Validator


configure_logs(verbose=True)
logging = get_logger()

class MarketOrder:
    """
    It handles buy/sell of the finance testnet
    """
    def __init__(self, bot: BinanceBot) -> None:
        """
        Initializes Market order with Binance bot client
        """
        self.bot = bot
        self.client = bot.client

    def place_order(
            self,
            symbol: str,
            side: str,
            quantity: float,
            leverage: int = 20
        ) -> dict | None:
        """
        Place a market order.

        :param symbol: Trading pair symbol (e.g., BTCUSDT)
        :param side: BUY or SELL
        :param quantity: Amount to trade
        :return: Order response dict or None if failed
        """
        symbol = symbol.upper()
        side = side.upper()


        try:
            logging.info(f"Placing Order | {side} | {quantity} | {symbol} | lev {leverage}")

            Validator.validate_symbol(symbol, self.client)
            Validator.validate_side(side)
            Validator.validate_order_params(symbol, quantity)
            Validator.validate_market_status(self.client)
            Validator.validate_leverage(leverage)
            Validator.validate_margin(self.client)

            self.client.futures_change_leverage(symbol=symbol, leverage=leverage)

            quantity = Validator.validate_quantity_bounds(
                symbol=symbol,
                quantity=quantity,
                client=self.client,
                leverage=leverage
            )

            if not quantity or quantity <= 0:
                logging.error("Order Aborted: Invalid quantity after validation")
                return None
            order = self.client.futures_create_order(
                symbol= symbol,
                quantity= quantity,
                side = side,
                type = "Market"
            )
            logging.info(f"Order Placed successfully with id: {order.get("orderId")}")
            return order

        except Exception as e:
            logging.error(f"Order failed {e}", exc_info=True)
            return None
