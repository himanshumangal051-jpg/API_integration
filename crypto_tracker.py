import argparse
from typing import Any

import requests

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
DEFAULT_TIMEOUT = 10


def fetch_coin_ids(query: str, timeout: int = DEFAULT_TIMEOUT) -> list[str]:
    try:
        response = requests.get(
            f"{COINGECKO_BASE_URL}/search",
            params={"query": query},
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Unable to fetch search data: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("Search response was not valid JSON") from exc

    coins = payload.get("coins")
    if not isinstance(coins, list):
        raise RuntimeError("Unexpected search response format")

    query_lower = query.strip().lower()
    matches = [
        coin.get("id")
        for coin in coins
        if isinstance(coin, dict)
        and isinstance(coin.get("id"), str)
        and (
            query_lower in str(coin.get("name", "")).lower()
            or query_lower in str(coin.get("symbol", "")).lower()
        )
    ]
    return matches


def fetch_market_data(
    coin_ids: list[str], currency: str, timeout: int = DEFAULT_TIMEOUT
) -> list[dict[str, Any]]:
    if not coin_ids:
        return []
    try:
        response = requests.get(
            f"{COINGECKO_BASE_URL}/coins/markets",
            params={
                "vs_currency": currency,
                "ids": ",".join(coin_ids),
                "order": "market_cap_desc",
                "per_page": len(coin_ids),
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "24h",
            },
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Unable to fetch market data: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("Market data response was not valid JSON") from exc

    if not isinstance(payload, list):
        raise RuntimeError("Unexpected market response format")
    return payload


def filter_market_data(
    market_data: list[dict[str, Any]], min_market_cap: float | None, limit: int
) -> list[dict[str, Any]]:
    filtered = market_data
    if min_market_cap is not None:
        filtered = [
            row
            for row in filtered
            if isinstance(row.get("market_cap"), (int, float))
            and float(row["market_cap"]) >= min_market_cap
        ]
    return filtered[:limit]


def format_rows(rows: list[dict[str, Any]], currency: str) -> str:
    if not rows:
        return "No matching coins found."

    name_width = 20
    symbol_width = 8
    price_width = 15
    market_cap_width = 18
    change_width = 12
    lines = [
        f"{'Name':{name_width}} {'Symbol':{symbol_width}} "
        f"{'Price':>{price_width}} {'Market Cap':>{market_cap_width}} {'24h Change':>{change_width}}",
        "-" * (name_width + symbol_width + price_width + market_cap_width + change_width + 4),
    ]
    symbol = currency.upper()
    for row in rows:
        lines.append(
            f"{str(row.get('name', 'N/A'))[:name_width]:{name_width}} "
            f"{str(row.get('symbol', 'N/A')).upper()[:symbol_width]:{symbol_width}} "
            f"{(f'{symbol} {float(row.get('current_price', 0)):.4f}'):>{price_width}} "
            f"{float(row.get('market_cap', 0)):>{market_cap_width},.0f} "
            f"{(f'{float(row.get('price_change_percentage_24h', 0)):.2f}%'):>{change_width}}"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch live cryptocurrency data.")
    parser.add_argument("--query", required=True, help="Coin name or symbol to search")
    parser.add_argument(
        "--currency", default="usd", help="Fiat currency for price display (default: usd)"
    )
    parser.add_argument(
        "--limit", type=int, default=5, help="Maximum number of results (default: 5)"
    )
    parser.add_argument(
        "--min-market-cap",
        type=float,
        default=None,
        help="Optional minimum market cap filter",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.limit <= 0:
        print("Error: --limit must be greater than 0.")
        return 1

    try:
        coin_ids = fetch_coin_ids(args.query)
        market_data = fetch_market_data(coin_ids, args.currency)
        filtered = filter_market_data(market_data, args.min_market_cap, args.limit)
        print(format_rows(filtered, args.currency))
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
