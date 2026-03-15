import json
import csv
import requests
from typing import List, Dict, Any, Tuple
from pathlib import Path


class Portfolio:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise ValueError(f"Config file not found: {config_path}")
        self.holdings: List[Dict[str, Any]] = self._load_holdings()
        self.prices: Dict[str, Dict[str, float]] = {}
        self.portfolio_data: List[Dict[str, float]] = []
        self.totals: Dict[str, float] = {}
        self.include_24hr_change = False

    def _load_holdings(self) -> List[Dict[str, Any]]:
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            coins = config.get('coins', [])
            if not coins:
                raise ValueError("No 'coins' key or empty coins list in config")
            holdings = []
            for coin in coins:
                holding = {
                    'coin_id': coin['id'],
                    'quantity': coin['quantity'],
                    'avg_buy_price': coin.get('avg_buy_price', 0.0)
                }
                holdings.append(holding)
            return holdings
        except Exception as e:
            raise ValueError(f"Invalid config file '{self.config_path}': {str(e)}")

    def refresh_prices(self, include_24hr_change: bool = False) -> None:
        self.include_24hr_change = include_24hr_change
        coin_ids = list(set(h['coin_id'] for h in self.holdings))
        self.prices = self._fetch_prices(coin_ids, include_24hr_change)
        self._compute_portfolio()

    def _fetch_prices(self, coin_ids: List[str], include_24hr: bool) -> Dict[str, Dict[str, float]]:
        if not coin_ids:
            return {}
        ids_str = ','.join(coin_ids)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd"
        if include_24hr:
            url += "&include_24hr_change=true"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch prices from CoinGecko: {str(e)}")

    def _compute_portfolio(self) -> None:
        self.portfolio_data = []
        total_value = 0.0
        total_invested = 0.0
        total_pnl_abs = 0.0
        for h in self.holdings:
            coin_id = h['coin_id']
            if coin_id not in self.prices:
                continue
            price_data = self.prices[coin_id]
            current_price = price_data['usd']
            change_24h = price_data.get('usd_24h_change', 0.0)
            quantity = float(h['quantity'])
            avg_buy_price = float(h['avg_buy_price'])
            current_value = quantity * current_price
            invested = quantity * avg_buy_price
            pnl_abs = current_value - invested
            pnl_pct = (pnl_abs / invested * 100) if invested > 0 else 0.0
            row = {
                'coin_id': coin_id,
                'quantity': quantity,
                'avg_buy_price': avg_buy_price,
                'current_price': current_price,
                'current_value': current_value,
                'pnl_abs': pnl_abs,
                'pnl_pct': pnl_pct,
                'change_24h': change_24h,
            }
            self.portfolio_data.append(row)
            total_value += current_value
            total_invested += invested
            total_pnl_abs += pnl_abs
        total_pnl_pct = (total_pnl_abs / total_invested * 100) if total_invested > 0 else 0.0
        self.totals = {
            'total_value': total_value,
            'total_invested': total_invested,
            'total_pnl_abs': total_pnl_abs,
            'total_pnl_pct': total_pnl_pct,
        }

    def get_rich_table(self) -> 'Table':
        from rich.table import Table
        from rich import box
        table = Table(title="Crypto Portfolio", box=box.ROUNDED)
        table.add_column("Coin", style="cyan", no_wrap=True)
        table.add_column("Quantity", justify="right")
        table.add_column("Price ($)", justify="right")
        table.add_column("Value ($)", justify="right")
        table.add_column("PnL ($)", justify="right")
        table.add_column("PnL %", justify="right")
        if self.include_24hr_change:
            table.add_column("24h %", justify="right")
        for row in self.portfolio_data:
            coin_name = row['coin_id'].upper()
            qty_str = f"{row['quantity']:.6f}".rstrip('0').rstrip('.')
            price_str = f"${row['current_price']:,.2f}"
            value_str = f"${row['current_value']:,.2f}"
            pnl_color = "green" if row['pnl_pct'] >= 0 else "red"
            pnl_abs_str = f"${row['pnl_abs']:,.2f}"
            pnl_pct_str = f"{row['pnl_pct']:+.2f}%"
            cells = [
                coin_name,
                qty_str,
                price_str,
                value_str,
                f"[{pnl_color}]{{pnl_abs_str}}[/{pnl_color}]",
                f"[{pnl_color}]{{pnl_pct_str}}[/{pnl_color}]",
            ]
            if self.include_24hr_change:
                h24_color = "green" if row['change_24h'] >= 0 else "red"
                h24_str = f"[{h24_color}]{row['change_24h']:+.2f}%[/{h24_color}]"
                cells.append(h24_str)
            table.add_row(*cells)
        if self.portfolio_data:
            total_color = "green" if self.totals['total_pnl_pct'] >= 0 else "red"
            cells = [
                "[bold]TOTAL[/bold]",
                "",
                "",
                f"${self.totals['total_value']:,.2f}",
                f"[{total_color} bold]${self.totals['total_pnl_abs']:,.2f}[/{total_color} bold]",
                f"[{total_color} bold]{self.totals['total_pnl_pct']:+.2f}%[/{total_color} bold]",
            ]
            if self.include_24hr_change:
                cells.append("")
            table.add_row(*cells)
        return table

    def get_totals(self) -> Tuple[float, float, float, float]:
        return (
            self.totals['total_value'],
            self.totals['total_invested'],
            self.totals['total_pnl_abs'],
            self.totals['total_pnl_pct'],
        )

    def export_to_csv(self, export_path: Path) -> None:
        fieldnames = ['coin_id', 'quantity', 'avg_buy_price', 'current_price', 'current_value', 'pnl_abs', 'pnl_pct']
        if self.include_24hr_change:
            fieldnames.append('change_24h')
        with open(export_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.portfolio_data)