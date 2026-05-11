"""
Tushare client for fetching stock price data.

This module provides integration with the Tushare API for stock price data.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import tushare as ts
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import settings


class TushareClient:
    """Client for interacting with Tushare API."""

    def __init__(self):
        """Initialize Tushare client with API token."""
        self.token = settings.tushare_token
        if not self.token:
            raise ValueError("TUSHARE_TOKEN not found in environment variables")

        ts.set_token(self.token)
        self.pro = ts.pro_api()
        self.cache_dir = settings.cache_path

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_stock_info(self, stock_code: str) -> Optional[Dict]:
        """
        Get basic stock information.

        Args:
            stock_code: Stock code (e.g., '600519')

        Returns:
            Dictionary with stock info or None if not found
        """
        # Determine exchange based on stock code
        ts_code = f"{stock_code}.SH" if stock_code.startswith("6") else f"{stock_code}.SZ"

        try:
            # Check cache first
            cache_key = f"tushare_stock_info_{stock_code}"
            cached = self._get_cache(cache_key)
            if cached:
                return cached

            df = self.pro.stock_basic(ts_code=ts_code)

            if df.empty:
                return None

            info = df.iloc[0].to_dict()

            # Add market prefix to code
            info["market"] = "SH" if stock_code.startswith("6") else "SZ"

            # Cache the result
            self._save_cache(cache_key, info)

            return info

        except Exception as e:
            print(f"Error fetching stock info for {stock_code}: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_daily_prices(
        self, stock_code: str, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Get daily price data for a stock.

        Args:
            stock_code: Stock code (e.g., '600519')
            start_date: Start date (YYYYMMDD format)
            end_date: End date (YYYYMMDD format)

        Returns:
            List of price data dictionaries
        """
        ts_code = f"{stock_code}.SH" if stock_code.startswith("6") else f"{stock_code}.SZ"

        # Default to last 3 months if no dates provided
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")

        try:
            # Check cache first
            cache_key = f"tushare_prices_{stock_code}_{start_date}_{end_date}"
            cached = self._get_cache(cache_key)
            if cached:
                return cached

            df = self.pro.daily(
                ts_code=ts_code, start_date=start_date, end_date=end_date, fields="trade_date,open,high,low,close,vol,amount"
            )

            if df.empty:
                return []

            # Sort by date ascending
            df = df.sort_values("trade_date")

            # Convert to list of dictionaries
            prices = df.to_dict("records")

            # Cache the result
            self._save_cache(cache_key, prices)

            return prices

        except Exception as e:
            print(f"Error fetching prices for {stock_code}: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_latest_price(self, stock_code: str) -> Optional[Dict]:
        """
        Get the latest price data for a stock.

        Args:
            stock_code: Stock code (e.g., '600519')

        Returns:
            Dictionary with latest price data or None
        """
        ts_code = f"{stock_code}.SH" if stock_code.startswith("6") else f"{stock_code}.SZ"

        try:
            # Check cache first (short expiry for latest price)
            cache_key = f"tushare_latest_price_{stock_code}"
            cached = self._get_cache(cache_key, max_age_hours=1)
            if cached:
                return cached

            df = self.pro.daily(
                ts_code=ts_code, fields="trade_date,open,high,low,close,vol,amount", limit=1
            )

            if df.empty:
                return None

            price_data = df.iloc[0].to_dict()

            # Cache with short expiry
            self._save_cache(cache_key, price_data)

            return price_data

        except Exception as e:
            print(f"Error fetching latest price for {stock_code}: {e}")
            return None

    def _get_cache(self, key: str, max_age_hours: int = 24) -> Optional[Dict]:
        """
        Get data from cache if not expired.

        Args:
            key: Cache key
            max_age_hours: Maximum age in hours

        Returns:
            Cached data or None if expired/not found
        """
        import json
        from pathlib import Path

        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Check if cache is expired
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                age = datetime.now() - file_time

                if age.total_seconds() < max_age_hours * 3600:
                    return data

            except (json.JSONDecodeError, IOError, KeyError):
                pass

        return None

    def _save_cache(self, key: str, data: Dict) -> None:
        """
        Save data to cache.

        Args:
            key: Cache key
            data: Data to cache
        """
        import json

        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except IOError:
            # Fail silently if caching fails
            pass
