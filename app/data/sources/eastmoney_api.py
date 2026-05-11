"""
Eastmoney API client for fetching financial statements.

This module provides integration with Eastmoney's data sources for financial statements.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import settings


class EastmoneyClient:
    """Client for interacting with Eastmoney data sources."""

    def __init__(self):
        """Initialize Eastmoney client."""
        self.api_key = settings.eastmoney_api_key
        self.cache_dir = settings.cache_path
        self.base_url = "http://datacenter-web.eastmoney.com/api"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_financial_statements(
        self, stock_code: str, report_type: str = "all"
    ) -> Optional[Dict[str, List[Dict]]]:
        """
        Get financial statements for a stock.

        Args:
            stock_code: Stock code (e.g., '600519')
            report_type: Type of report ('income', 'balance', 'cash', or 'all')

        Returns:
            Dictionary containing financial statement data
        """
        # Determine market prefix
        market = "1" if stock_code.startswith("6") else "0"  # 1=SH, 0=SZ

        try:
            # Check cache first
            cache_key = f"eastmoney_financials_{stock_code}"
            cached = self._get_cache(cache_key, max_age_hours=168)  # 7 days
            if cached:
                return cached

            # Eastmoney API endpoint for financial statements
            url = f"{self.base_url}/data/v1/get"

            # Get income statement
            income_data = self._fetch_statement(stock_code, market, "RZLZ")  # RZLZ = Income Statement

            # Get balance sheet
            balance_data = self._fetch_statement(stock_code, market, "ZCFZB")  # ZCFZB = Balance Sheet

            # Get cash flow statement
            cash_data = self._fetch_statement(stock_code, market, "XJLLB")  # XJLLB = Cash Flow

            result = {
                "income": income_data,
                "balance": balance_data,
                "cash": cash_data,
            }

            # Cache the result
            self._save_cache(cache_key, result)

            return result

        except Exception as e:
            print(f"Error fetching financial statements for {stock_code}: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _fetch_statement(self, stock_code: str, market: str, report_type: str) -> List[Dict]:
        """
        Fetch a specific financial statement from Eastmoney.

        Args:
            stock_code: Stock code
            market: Market identifier (1=SH, 0=SZ)
            report_type: Type of report

        Returns:
            List of statement data dictionaries
        """
        url = f"{self.base_url}/data/v1/get"
        params = {
            "sortColumns": "REPORT_DATE",
            "sortTypes": "-1",
            "pageSize": "20",
            "pageNumber": "1",
            "reportName": report_type,
            "columns": "ALL",
            "filter": f"(SECUCODE=\"{market}.{stock_code}\")",
            "source": "WEB",
            "client": "WEB",
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        if data.get("success") and data.get("result"):
            return data["result"]["data"]

        return []

    def parse_financial_metrics(self, financial_data: Dict) -> Dict[str, float]:
        """
        Parse financial statements and calculate key metrics.

        Args:
            financial_data: Raw financial statement data

        Returns:
            Dictionary of calculated financial metrics
        """
        if not financial_data or not financial_data.get("income"):
            return {}

        try:
            # Get the most recent period data
            latest_income = financial_data["income"][0] if financial_data["income"] else {}
            latest_balance = financial_data["balance"][0] if financial_data.get("balance") else {}
            latest_cash = financial_data["cash"][0] if financial_data.get("cash") else {}

            # Calculate metrics (field names may vary, these are common ones)
            metrics = {
                "revenue": self._safe_float(latest_income.get("TOTAL_OPERATE_INCOME", 0)),
                "net_profit": self._safe_float(latest_income.get("PARENT_NETPROFIT", 0)),
                "gross_profit": self._safe_float(latest_income.get("TOTAL_OPERATE_COST", 0)),
                "operating_profit": self._safe_float(latest_income.get("OPERATE_PROFIT", 0)),
                "total_assets": self._safe_float(latest_balance.get("TOTAL_ASSETS", 0)),
                "total_liabilities": self._safe_float(latest_balance.get("TOTAL_LIABILITIES", 0)),
                "total_equity": self._safe_float(latest_balance.get("TOTAL_EQUITY", 0)),
                "operating_cash_flow": self._safe_float(latest_cash.get("TOTAL_CASHFL_PS", 0)),
                "investing_cash_flow": self._safe_float(latest_cash.get("INVEST_CASHFL_PS", 0)),
                "financing_cash_flow": self._safe_float(latest_cash.get("FINAN_CASHFL_PS", 0)),
            }

            # Calculate derived metrics
            metrics["gross_profit"] = max(
                0, metrics["revenue"] - metrics.get("cost_of_sales", 0)
            )  # Adjust as needed

            # Calculate ratios
            if metrics["total_equity"] > 0:
                metrics["roe"] = (metrics["net_profit"] / metrics["total_equity"]) * 100
            else:
                metrics["roe"] = 0

            if metrics["total_assets"] > 0:
                metrics["roa"] = (metrics["net_profit"] / metrics["total_assets"]) * 100
                metrics["debt_ratio"] = metrics["total_liabilities"] / metrics["total_assets"]
            else:
                metrics["roa"] = 0
                metrics["debt_ratio"] = 0

            if metrics["revenue"] > 0:
                metrics["net_margin"] = (metrics["net_profit"] / metrics["revenue"]) * 100
                metrics["gross_margin"] = (metrics["gross_profit"] / metrics["revenue"]) * 100
            else:
                metrics["net_margin"] = 0
                metrics["gross_margin"] = 0

            # Get previous period for growth calculation
            if len(financial_data.get("income", [])) > 1:
                prev_income = financial_data["income"][1]
                prev_revenue = self._safe_float(prev_income.get("TOTAL_OPERATE_INCOME", 0))

                if prev_revenue > 0:
                    metrics["revenue_growth"] = ((metrics["revenue"] - prev_revenue) / prev_revenue) * 100
                else:
                    metrics["revenue_growth"] = 0
            else:
                metrics["revenue_growth"] = 0

            return metrics

        except Exception as e:
            print(f"Error parsing financial metrics: {e}")
            return {}

    def _safe_float(self, value: any) -> float:
        """Safely convert value to float."""
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

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
