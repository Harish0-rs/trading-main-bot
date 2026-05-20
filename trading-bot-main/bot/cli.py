from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt

from bot.display import (
    console,
    print_cancel_response,
    print_error,
    print_main_menu,
    print_open_orders,
    print_order_history,
    print_order_response,
    print_order_summary,
    print_positions,
    print_price,
    print_balance,
    print_success,
)
from bot.logging_config import setup_logging
from bot.orders import OrderManager

app = typer.Typer(
    name="trading-bot",
    help="⚡ Binance USDT-M Futures Testnet CLI Trading Bot",
    add_completion=False,
    rich_markup_mode="rich",
)


def _get_manager() -> OrderManager:
    try:
        return OrderManager()
    except RuntimeError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------


@app.command("price")
def cmd_price(
    symbol: str = typer.Argument(..., help="Trading pair symbol, e.g. BTCUSDT"),
) -> None:
    """Fetch the current mark price for a symbol."""
    setup_logging()
    manager = _get_manager()
    try:
        data = manager.get_price(symbol)
        print_price(data["symbol"], data["price"])
    except RuntimeError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


@app.command("balance")
def cmd_balance() -> None:
    """Display your Binance Futures account balance."""
    setup_logging()
    manager = _get_manager()
    try:
        balances = manager.get_balance()
        if not balances:
            console.print("[dim]No non-zero balances found.[/]")
        else:
            print_balance(balances)
    except RuntimeError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


@app.command("positions")
def cmd_positions() -> None:
    """List currently open positions."""
    setup_logging()
    manager = _get_manager()
    try:
        positions = manager.get_positions()
        if not positions:
            console.print("[dim]No open positions.[/]")
        else:
            print_positions(positions)
    except RuntimeError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


@app.command("open-orders")
def cmd_open_orders(
    symbol: Optional[str] = typer.Option(None, "--symbol", "-s", help="Filter by symbol"),
) -> None:
    """List open orders (optionally filtered by symbol)."""
    setup_logging()
    manager = _get_manager()
    try:
        orders = manager.get_open_orders(symbol)
        if not orders:
            console.print("[dim]No open orders.[/]")
        else:
            print_open_orders(orders)
    except RuntimeError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


@app.command("order")
def cmd_order(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair, e.g. BTCUSDT"),
    side: str = typer.Option(..., "--side", help="BUY or SELL"),
    order_type: str = typer.Option(..., "--type", "-t", help="MARKET, LIMIT, or STOP_MARKET"),
    quantity: float = typer.Option(..., "--qty", "-q", help="Order quantity"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Limit price (LIMIT orders)"),
    stop_price: Optional[float] = typer.Option(None, "--stop-price", help="Stop price (STOP_MARKET orders)"),
    confirm: bool = typer.Option(True, "--confirm/--no-confirm", help="Prompt for confirmation before placing"),
) -> None:
    """Place a new futures order."""
    setup_logging()
    manager = _get_manager()
    try:
        # Build a preview params dict for display before calling place_order
        from bot.validators import validate_order_params
        params = validate_order_params(symbol, side, order_type, quantity, price, stop_price)
    except ValueError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)

    print_order_summary(params)

    if confirm:
        answer = Prompt.ask("[yellow]Confirm order?[/] [dim](yes/no)[/]", default="no")
        if answer.lower() not in {"yes", "y"}:
            console.print("[dim]Order cancelled by user.[/]")
            raise typer.Exit()

    try:
        placed_params, response = manager.place_order(
            symbol=params["symbol"],
            side=params["side"],
            order_type=params["order_type"],
            quantity=params["quantity"],
            price=params.get("price"),
            stop_price=params.get("stop_price"),
        )
        print_order_response(response)
    except (RuntimeError, ValueError) as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


@app.command("cancel")
def cmd_cancel(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair, e.g. BTCUSDT"),
    order_id: int = typer.Option(..., "--order-id", "-i", help="Order ID to cancel"),
) -> None:
    """Cancel an open order by symbol and order ID."""
    setup_logging()
    manager = _get_manager()
    try:
        response = manager.cancel_order(symbol, order_id)
        print_cancel_response(response)
    except RuntimeError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


@app.command("history")
def cmd_history(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair, e.g. BTCUSDT"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of historical orders to fetch (max 500)"),
) -> None:
    """Fetch order history for a symbol."""
    setup_logging()
    manager = _get_manager()
    try:
        orders = manager.get_order_history(symbol, limit)
        if not orders:
            console.print("[dim]No order history found.[/]")
        else:
            print_order_history(orders)
    except RuntimeError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# Interactive menu mode
# ---------------------------------------------------------------------------


@app.command("menu")
def cmd_menu() -> None:
    """Launch the interactive terminal menu."""
    setup_logging()
    manager = _get_manager()

    while True:
        console.print()
        print_main_menu()
        choice = Prompt.ask("\n[bold cyan]Select option[/] [dim](0–7)[/]", default="0").strip()

        if choice == "0":
            console.print("[dim]Goodbye![/]")
            break

        elif choice == "1":
            _menu_place_order(manager)

        elif choice == "2":
            symbol = _prompt_symbol(manager)
            if symbol:
                try:
                    data = manager.get_price(symbol)
                    print_price(data["symbol"], data["price"])
                except RuntimeError as exc:
                    print_error(str(exc))

        elif choice == "3":
            try:
                balances = manager.get_balance()
                if not balances:
                    console.print("[dim]No non-zero balances found.[/]")
                else:
                    print_balance(balances)
            except RuntimeError as exc:
                print_error(str(exc))

        elif choice == "4":
            try:
                positions = manager.get_positions()
                if not positions:
                    console.print("[dim]No open positions.[/]")
                else:
                    print_positions(positions)
            except RuntimeError as exc:
                print_error(str(exc))

        elif choice == "5":
            console.print("[dim]Leave symbol blank to see all open orders.[/]")
            symbol_filter = _prompt_symbol(manager, optional=True)
            try:
                orders = manager.get_open_orders(symbol_filter or None)
                if not orders:
                    console.print("[dim]No open orders.[/]")
                else:
                    print_open_orders(orders)
            except RuntimeError as exc:
                print_error(str(exc))

        elif choice == "6":
            _menu_cancel_order(manager)

        elif choice == "7":
            symbol = _prompt_symbol(manager)
            if symbol:
                limit_str = Prompt.ask("[cyan]How many records?[/]", default="10")
                try:
                    orders = manager.get_order_history(symbol, int(limit_str))
                    if not orders:
                        console.print("[dim]No order history found.[/]")
                    else:
                        print_order_history(orders)
                except (RuntimeError, ValueError) as exc:
                    print_error(str(exc))

        else:
            print_error(f"Unknown option: {choice!r}. Enter a number 0–7.")


def _prompt_symbol(manager: OrderManager, optional: bool = False) -> str:
    """Show available testnet symbols then prompt the user to pick one."""
    console.print("[dim]Fetching available symbols from testnet…[/]")
    try:
        symbols = manager.get_symbols()
        # Display in rows of 6
        rows = ["  ".join(symbols[i:i+6]) for i in range(0, len(symbols), 6)]
        console.print("[bold green]Available symbols:[/]")
        for row in rows:
            console.print(f"  [cyan]{row}[/]")
    except RuntimeError:
        console.print("[yellow]⚠ Could not fetch symbol list — type manually.[/]")

    placeholder = "[dim](or press Enter to skip)[/]" if optional else ""
    return Prompt.ask(f"[cyan]Symbol[/] {placeholder}", default="").strip().upper()


def _menu_place_order(manager: OrderManager) -> None:
    console.print("[bold]Place Order[/]")
    symbol = _prompt_symbol(manager)
    if not symbol:
        print_error("Symbol is required.")
        return

    side = Prompt.ask("[cyan]Side[/]", choices=["BUY", "SELL"])
    order_type = Prompt.ask("[cyan]Type[/]", choices=["MARKET", "LIMIT", "STOP_MARKET"])
    qty_str = Prompt.ask("[cyan]Quantity[/]")

    price: float | None = None
    stop_price: float | None = None

    if order_type == "LIMIT":
        price_str = Prompt.ask("[cyan]Limit Price[/]")
        try:
            price = float(price_str)
        except ValueError:
            print_error(f"Invalid price: {price_str!r}")
            return

    if order_type == "STOP_MARKET":
        sp_str = Prompt.ask("[cyan]Stop Price[/]")
        try:
            stop_price = float(sp_str)
        except ValueError:
            print_error(f"Invalid stop price: {sp_str!r}")
            return

    try:
        quantity = float(qty_str)
    except ValueError:
        print_error(f"Invalid quantity: {qty_str!r}")
        return

    try:
        from bot.validators import validate_order_params
        preview = validate_order_params(symbol, side, order_type, quantity, price, stop_price)
    except ValueError as exc:
        print_error(str(exc))
        return

    print_order_summary(preview)
    confirm = Prompt.ask("[yellow]Confirm?[/]", choices=["yes", "no"], default="no")
    if confirm != "yes":
        console.print("[dim]Order discarded.[/]")
        return

    try:
        _, response = manager.place_order(
            symbol=preview["symbol"],
            side=preview["side"],
            order_type=preview["order_type"],
            quantity=preview["quantity"],
            price=preview.get("price"),
            stop_price=preview.get("stop_price"),
        )
        print_order_response(response)
    except (RuntimeError, ValueError) as exc:
        print_error(str(exc))


def _menu_cancel_order(manager: OrderManager) -> None:
    symbol = Prompt.ask("[cyan]Symbol[/]")
    order_id_str = Prompt.ask("[cyan]Order ID[/]")
    try:
        order_id = int(order_id_str)
    except ValueError:
        print_error(f"Invalid order ID: {order_id_str!r}")
        return
    try:
        response = manager.cancel_order(symbol, order_id)
        print_cancel_response(response)
    except RuntimeError as exc:
        print_error(str(exc))
