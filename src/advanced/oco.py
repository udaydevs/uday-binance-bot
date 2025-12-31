"""
Improved OCO Orders: Auto-detect price and prevent trigger errors.
"""

from src.utils.logging import configure_logs, get_logger
from ..client import BinanceBot

configure_logs(verbose=True)
logging = get_logger()

class OCOOrder:
    """
    Automated One-Cancels-the-Other (OCO) style logic for futures trading.

    This class monitors live market prices and automatically calculates the
    optimal Take Profit (TP) and Stop Loss (SL) levels. It then places two
    linked orders:
    - A STOP_MARKET order for the Stop Loss (SL)
    - A TAKE_PROFIT_MARKET order for the Take Profit (TP)

    When one order is triggered, the other is automatically canceled,
    helping manage risk and lock in profits efficiently.
    """

    def __init__(self, bot: BinanceBot) -> None:
        """
        Initialized OCOOrder with Binance Bot client
        """
        self.bot = bot
        self.client = bot.client

    def get_price(self, symbol: str) -> float:
        """
        This function is used to fetch the current price of the symbol
        in the future market
        """
        price = float(self.client.futures_symbol_ticker(symbol=symbol)["price"])
        logging.info(f"Live {symbol} price:{ price}")
        return price

    def place_oco(
        self,
        symbol: str,
        side: str,
        quantity: float,
        tp_percent: float = 2,
        sl_percent: float = 2
    ) -> dict | None:
        """
        Create a dual-order setup simulating an OCO structure in Binance Futures
        """
        symbol = symbol.upper()
        side = side.upper()

        if side not in ["BUY", "SELL"]:
            logging.error("OCO Error: Only BUY or SELL allowed.")
            return None

        current_price = self.get_price(symbol)

        if side == "BUY":
            tp = round(current_price * (1 + tp_percent / 100))
            sl = round(current_price * (1 - sl_percent / 100))

            if sl >= current_price:
                logging.error("SL must be BELOW current market price for BUY position")
                raise ValueError("Stop Loss placement invalid for BUY order")
            if tp <= current_price:
                logging.error("TP must be ABOVE current market price for BUY position")
                raise ValueError("Take Profit placement invalid for BUY order")

            order_side = "SELL"
        else:
            tp = round(current_price * (1 - tp_percent / 100))
            sl = round(current_price * (1 + sl_percent / 100))

            if sl <= current_price:
                logging.error("SL must be ABOVE current market price for SELL position")
                raise ValueError("Stop Loss placement invalid for SELL order")
            if tp >= current_price:
                logging.error("TP must be BELOW current market price for SELL position")
                raise ValueError("Take Profit placement invalid for SELL order")
            
            order_side = "BUY"

        logging.info(
            f"OCO Setup for {symbol} {side}: Qty {quantity} | TP: {tp} | SL: {sl}"
        )

        try:
            sl_order = self.client.futures_create_order(
                symbol=symbol,
                side=order_side,
                type="STOP_MARKET",
                stopPrice=sl,
                closePosition=False,
                quantity=quantity
            )

            tp_order = self.client.futures_create_order(
                symbol=symbol,
                side=order_side,
                type="TAKE_PROFIT_MARKET",
                stopPrice=tp,
                closePosition=False,
                quantity=quantity
            )

            logging.info("OCO Orders Active: TP and SL Placed Successfully")
            res = {"stop_loss": sl_order, "take_profit": tp_order}
            return res

        except Exception as err:
            logging.error(f"OCO Failed:{err}")
            return None
