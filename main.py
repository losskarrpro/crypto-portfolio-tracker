#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box
from portfolio import Portfolio


def main():
    parser = argparse.ArgumentParser(
        description="Crypto Portfolio Tracker CLI - Track your crypto holdings with live prices from CoinGecko."
    )
    parser.add_argument(
        "--config", "-c", default="config.json", help="Path to config JSON file (default: config.json)"
    )
    parser.add_argument(
        "--export", "-e", help="Export current portfolio data to CSV file"
    )
    parser.add_argument(
        "--daily", "-d", action="store_true", help="Show daily (24h) stats in the table"
    )
    args = parser.parse_args()

    console = Console()
    config_path = Path(args.config)

    if not config_path.exists():
        console.print(f"[red]Error: Config file '{args.config}' not found.[/red]")
        sys.exit(1)

    try:
        portfolio = Portfolio(str(config_path))
        portfolio.refresh_prices(include_24hr_change=args.daily)

        table = portfolio.get_rich_table()
        console.print(table)

        total_value, total_invested, total_pnl_abs, total_pnl_pct = portfolio.get_totals()
        pnl_color = "green" if total_pnl_pct >= 0 else "red"
        console.print(
            f"\n[bold cyan]Summary:[/bold cyan]"
            f"\nTotal Invested: [bold yellow]${total_invested:,.2f}[/bold yellow]"
            f"\nTotal Value: [bold cyan]${total_value:,.2f}[/bold cyan]"
            f"\nTotal PnL: [{pnl_color}]${total_pnl_abs:,.2f} ({total_pnl_pct:+.2f}%)[/{pnl_color}]"
        )

        if args.export:
            export_path = Path(args.export)
            portfolio.export_to_csv(export_path)
            console.print(f"[green]✓ Exported to '{export_path}'[/green]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()