"""
Configuration management for the Stock Analysis System.

This module handles environment variable loading and application settings.
"""
from pathlib import Path
from typing import List, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Credentials
    tushare_token: str = ""
    eastmoney_api_key: str = ""

    # Cache Configuration
    cache_dir: str = "./cache"
    cache_expiry_price: int = 24  # hours
    cache_expiry_financials: int = 168  # 7 days
    cache_expiry_news: int = 4  # hours

    # API Configuration
    caixin_rate_limit: int = 60  # seconds between requests

    # Application Configuration
    app_name: str = "Stock Analysis System"
    app_version: str = "1.0.0"
    debug: bool = False

    # Focus Industries
    focus_industries: List[str] = [
        "AI",
        "Robotics",
        "Military Industry",
        "Electricity & New Energy",
        "Biopharmaceutical",
    ]

    # Analysis Weights
    weight_macro: float = 0.3
    weight_fundamental: float = 0.4
    weight_technical: float = 0.3

    # Demo Stocks
    demo_stocks: dict = {
        "AI": {"code": "002230", "name": "科大讯飞", "description": "Speech recognition AI leader"},
        "Robotics": {
            "code": "002747",
            "name": "埃斯顿",
            "description": "Industrial robotics manufacturer",
        },
        "Military": {
            "code": "600760",
            "name": "中航沈飞",
            "description": "Aviation and defense manufacturing",
        },
        "Energy": {"code": "300750", "name": "宁德时代", "description": "Battery and new energy technology"},
        "Biopharma": {
            "code": "600276",
            "name": "恒瑞医药",
            "description": "Pharmaceutical innovation leader",
        },
    }

    @property
    def cache_path(self) -> Path:
        """Get the cache directory as a Path object."""
        path = Path(self.cache_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_cache_file_path(self, cache_type: str, identifier: str) -> Path:
        """
        Get the cache file path for a specific cache type and identifier.

        Args:
            cache_type: Type of cache (e.g., 'price', 'financial', 'news')
            identifier: Unique identifier (e.g., stock code)

        Returns:
            Path object for the cache file
        """
        return self.cache_path / f"{cache_type}_{identifier}.json"


# Global settings instance
settings = Settings()
