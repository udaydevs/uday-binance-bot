#!/usr/bin/env python3
"""
Binance Futures Trading Bot CLI
"""
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.tree import Tree
from rich import box

from bot.client import BinanceBot
from bot.market_order import MarketOrder
from bot.limit_order import LimitOrder
from bot.advanced.oco import OCOOrder

console = Console()
LOG_PATH = Path("logs")


def configure_logging(verbose: bool = False) -> None:
    """
    Docstring for configure_logging
    
    :param verbose: Description
    :type verbose: bool
    """
    LOG_PATH.mkdir(exist_ok=True)
    log_file = LOG_PATH / f"bot_{datetime.now():%Y%m%d}.log"

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )


def banner() -> None:
    """
    Docstring for banner
    """
    panel = Panel.fit(
            "Binance Futures Trading CLI",
            title="Trading Bot",
            border_style="cyan",
        )
    console.print(Align.center(panel))


def result_table(title: str, data: Dict) -> None:
    """Create a table"""
    if not data:
        console.print("No response received. Check logs.")
        return

    table = Table(
        title=title,
        box=box.ROUNDED,
        header_style="bold cyan",
        border_style="blue",
    )

    table.add_column("Field", justify="left")
    table.add_column("Value", justify="left")
    for key, value in data.items():
        table.add_row(key, str(value))

    console.print(table)
    console.print()


def input_values(limit=False, oco=False):
    """
    Input values are defined here
    """
    symbol = Prompt.ask("Symbol", default="BTCUSDT").upper()
    side = Prompt.ask("Side", choices=["BUY", "SELL"]).upper()
    qty = float(Prompt.ask("Quantity"))

    price = tp = sl = None

    if limit:
        price = float(Prompt.ask("Limit Price"))

    if oco:
        tp = float(Prompt.ask("Take Profit %", default="2"))
        sl = float(Prompt.ask("Stop Loss %", default="2"))

    return symbol, side, qty, price, tp, sl


def handle_market(bot: BinanceBot) -> None:
    """
    Handle Market Order
    """
    symbol, side, qty, *_ = input_values()

    if Confirm.ask("Confirm order execution?"):
        res = MarketOrder(bot).place_order(symbol, side, qty)
        result_table("Market Order Result", res)


def handle_limit(bot: BinanceBot) -> None:
    """
    Handle Limit Order
    """
    symbol, side, qty, price, *_ = input_values(limit=True)

    if Confirm.ask("Confirm order execution?"):
        res = LimitOrder(bot).place_limit_order(symbol, side, qty, price)
        result_table("Limit Order Result", res)


def handle_oco(bot: BinanceBot) -> None:
    """
    Handle OCO Order
    """
    symbol, side, qty, _, tp, sl = input_values(oco=True)

    if Confirm.ask("Confirm order execution?"):
        res = OCOOrder(bot).place_oco(symbol, side, qty, tp, sl)
        result_table("OCO STOP Order", res.get('stop_loss'))
        result_table("OCO Target Profit Order", res.get('target_profit'))


def connection_status(bot: BinanceBot) -> None:
    """
    Check connection status
    """
    with Progress(SpinnerColumn(), TextColumn("Checking connection...")) as p:
        p.add_task("", total=None)
        status = bot.check_connection()

    if status:
        console.print("Connection successful")
    else:
        console.print("Connection failed")


def interactive_menu(bot: BinanceBot) -> None:
    """
    A menu is defined here
    """
    while True:
        tree = Tree("Main Menu")
        trading = tree.add("Trading")
        trading.add("1. Market Order")
        trading.add("2. Limit Order")
        trading.add("3. OCO Order")
        tree.add("4. Check Connection")
        tree.add("0. Exit")

        console.print(Panel(tree, border_style="cyan"))
        choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4"])
        console.print()

        if choice == "1":
            handle_market(bot)
        elif choice == "2":
            handle_limit(bot)
        elif choice == "3":
            handle_oco(bot)
        elif choice == "4":
            connection_status(bot)
        elif choice == "0":
            console.print("Exiting.")
            return


def execute_command(bot: BinanceBot, args: argparse.Namespace) -> None:
    """
    Execution of commands are defined here
    """
    if args.command == "market":
        res = MarketOrder(bot).place_order(args.symbol, args.side, args.qty)
        result_table("Market Order", res)

    elif args.command == "limit":
        res = LimitOrder(bot).place_limit_order(args.symbol, args.side, args.qty, args.price)
        result_table("Limit Order", res)

    elif args.command == "oco":
        res = OCOOrder(bot).place_oco(args.symbol, args.side, args.qty, args.tp, args.sl)
        result_table("OCO STOP Order", res.get('stop_loss'))
        result_table("OCO Target Profit Order", res.get('target_profit'))




def build_parser() -> argparse.ArgumentParser:
    """
    Argument parsers are intialized
    """
    parser = argparse.ArgumentParser(description="Binance Trading CLI")

    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive menu mode")
    parser.add_argument("--testnet", action="store_true", default=True)
    parser.add_argument("-v", "--verbose", action="store_true")

    sub = parser.add_subparsers(dest="command")

    m = sub.add_parser("market")
    m.add_argument("--symbol", required=True)
    m.add_argument("--side", required=True)
    m.add_argument("--qty", required=True, type=float)

    l = sub.add_parser("limit")
    l.add_argument("--symbol", required=True)
    l.add_argument("--side", required=True)
    l.add_argument("--qty", required=True, type=float)
    l.add_argument("--price", required=True, type=float)

    o = sub.add_parser("oco")
    o.add_argument("--symbol", required=True)
    o.add_argument("--side", required=True)
    o.add_argument("--qty", required=True, type=float)
    o.add_argument("--tp", default=2, type=float)
    o.add_argument("--sl", default=2, type=float)

    return parser


def main() -> None:
    """
    Docstring for main
    """
    parser = build_parser()
    args = parser.parse_args()

    configure_logging(verbose=args.verbose)
    banner()

    bot = BinanceBot(testnet=args.testnet)

    if not bot.check_connection():
        console.print("API Connection failed. Check credentials.")
        sys.exit(1)

    if args.interactive or not args.command:
        return interactive_menu(bot)

    execute_command(bot, args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("Operation cancelled.")
        sys.exit(130)
    except Exception as error:
        logging.exception("Fatal error")
        console.print(f"Fatal Error: {error}")
        sys.exit(1)
