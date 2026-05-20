from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

SIDE_COLORS = {"BUY": "green", "SELL": "red"}


def print_success(message: str) -> None:
    console.print(f"[bold green]✔[/] {message}")


def print_error(message: str) -> None:
    console.print(f"[bold red]✘[/] {message}")


def print_price(symbol: str, price: str) -> None:
    console.print(
        Panel(
            f"[bold white]{symbol}[/]  [bold yellow]{price}[/]",
            title="[cyan]Live Price[/]",
            border_style="cyan",
            expand=False,
        )
    )


def print_balance(balances: list[dict]) -> None:
    table = Table(title="Account Balance", box=box.ROUNDED, border_style="blue", show_lines=True)
    table.add_column("Asset", style="bold white")
    table.add_column("Wallet Balance", justify="right", style="yellow")
    table.add_column("Available Balance", justify="right", style="green")
    table.add_column("Unrealized PnL", justify="right")

    for item in balances:
        pnl = float(item.get("crossUnPnl", 0))
        pnl_style = "green" if pnl >= 0 else "red"
        table.add_row(
            item["asset"],
            item["balance"],
            item["availableBalance"],
            f"[{pnl_style}]{pnl:.4f}[/]",
        )
    console.print(table)


def print_positions(positions: list[dict]) -> None:
    table = Table(title="Open Positions", box=box.ROUNDED, border_style="magenta", show_lines=True)
    table.add_column("Symbol", style="bold white")
    table.add_column("Side", justify="center")
    table.add_column("Size", justify="right", style="yellow")
    table.add_column("Entry Price", justify="right")
    table.add_column("Mark Price", justify="right")
    table.add_column("Unrealized PnL", justify="right")
    table.add_column("Leverage", justify="center", style="cyan")

    for pos in positions:
        amt = float(pos.get("positionAmt", 0))
        side = "LONG" if amt > 0 else "SHORT"
        side_color = "green" if amt > 0 else "red"
        pnl = float(pos.get("unRealizedProfit", 0))
        pnl_style = "green" if pnl >= 0 else "red"
        table.add_row(
            pos["symbol"],
            f"[{side_color}]{side}[/]",
            str(abs(amt)),
            pos.get("entryPrice", "—"),
            pos.get("markPrice", "—"),
            f"[{pnl_style}]{pnl:.4f}[/]",
            f"{pos.get('leverage', '—')}x",
        )
    console.print(table)


def print_open_orders(orders: list[dict]) -> None:
    table = Table(title="Open Orders", box=box.ROUNDED, border_style="yellow", show_lines=True)
    table.add_column("Order ID", style="dim")
    table.add_column("Symbol", style="bold white")
    table.add_column("Side", justify="center")
    table.add_column("Type", justify="center")
    table.add_column("Qty", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Status", justify="center")

    for order in orders:
        side = order.get("side", "")
        color = SIDE_COLORS.get(side, "white")
        table.add_row(
            str(order.get("orderId", "")),
            order.get("symbol", ""),
            f"[{color}]{side}[/]",
            order.get("type", ""),
            order.get("origQty", ""),
            order.get("price", "—"),
            order.get("status", ""),
        )
    console.print(table)


def print_order_summary(params: dict) -> None:
    table = Table(title="Order Summary", box=box.SIMPLE_HEAVY, border_style="dim white", show_lines=False)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="bold white")

    side_color = SIDE_COLORS.get(params.get("side", ""), "white")
    table.add_row("Symbol", params.get("symbol", ""))
    table.add_row("Side", f"[{side_color}]{params.get('side', '')}[/]")
    table.add_row("Type", params.get("order_type", ""))
    table.add_row("Quantity", str(params.get("quantity", "")))
    if params.get("price"):
        table.add_row("Price", str(params["price"]))
    if params.get("stop_price"):
        table.add_row("Stop Price", str(params["stop_price"]))
    console.print(table)


def print_order_response(response: dict) -> None:
    table = Table(title="Order Placed", box=box.ROUNDED, border_style="green", show_lines=True)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="bold white")

    side = response.get("side", "")
    side_color = SIDE_COLORS.get(side, "white")
    rows = [
        ("Order ID", str(response.get("orderId", ""))),
        ("Symbol", response.get("symbol", "")),
        ("Side", f"[{side_color}]{side}[/]"),
        ("Type", response.get("type", "")),
        ("Quantity", str(response.get("origQty", ""))),
        ("Price", str(response.get("price", ""))),
        ("Status", response.get("status", "")),
        ("Time in Force", response.get("timeInForce", "")),
    ]
    for field, value in rows:
        table.add_row(field, value)
    console.print(table)


def print_cancel_response(response: dict) -> None:
    console.print(
        Panel(
            f"[yellow]Order [bold]{response.get('orderId')}[/] for [bold]{response.get('symbol')}[/] cancelled.[/]",
            title="[red]Order Cancelled[/]",
            border_style="red",
            expand=False,
        )
    )


def print_order_history(orders: list[dict]) -> None:
    table = Table(title="Order History", box=box.ROUNDED, border_style="blue", show_lines=True)
    table.add_column("Order ID", style="dim")
    table.add_column("Symbol", style="bold white")
    table.add_column("Side", justify="center")
    table.add_column("Type", justify="center")
    table.add_column("Qty", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Status", justify="center")

    for order in orders:
        side = order.get("side", "")
        color = SIDE_COLORS.get(side, "white")
        table.add_row(
            str(order.get("orderId", "")),
            order.get("symbol", ""),
            f"[{color}]{side}[/]",
            order.get("type", ""),
            order.get("origQty", ""),
            order.get("price", "—"),
            order.get("status", ""),
        )
    console.print(table)


def print_main_menu() -> None:
    lines = [
        "[bold white]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]",
        "[bold cyan]  1.[/]  Place Order (BUY / SELL)",
        "[bold cyan]  2.[/]  Get Live Price",
        "[bold cyan]  3.[/]  View Account Balance",
        "[bold cyan]  4.[/]  View Open Positions",
        "[bold cyan]  5.[/]  View Open Orders",
        "[bold cyan]  6.[/]  Cancel an Order",
        "[bold cyan]  7.[/]  Order History",
        "[bold white]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]",
        "[bold red]  0.[/]  Exit",
    ]
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold magenta]⚡ Trading Bot — Main Menu[/]",
            subtitle="[dim]Enter the number of your choice[/]",
            border_style="magenta",
            expand=False,
            padding=(1, 4),
        )
    )
