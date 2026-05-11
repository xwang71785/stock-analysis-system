"""
Base analyst class for the Stock Analysis System.

This module provides the abstract base class that all analyst modules must inherit from.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.config.settings import settings


class BaseAnalyst(ABC):
    """
    Abstract base class for all analyst modules.

    All analyst implementations (Macro, Fundamental, Technical) must inherit from this class
    and implement the required abstract methods.
    """

    def __init__(self, stock_code: str):
        """
        Initialize the analyst.

        Args:
            stock_code: The stock code to analyze (e.g., '600519')
        """
        self.stock_code = stock_code
        self.settings = settings
        self.cache_dir = settings.cache_path

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        Perform the analysis and return results.

        This is the main method that each analyst must implement. It should:
        1. Fetch required data
        2. Perform analysis calculations
        3. Return a dictionary with analysis results

        Returns:
            Dictionary containing analysis results
        """
        pass

    def get_cached_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached data if available.

        Args:
            cache_key: Unique identifier for the cached data

        Returns:
            Cached data dictionary or None if not found
        """
        import json
        from pathlib import Path

        cache_file = self.cache_dir / cache_key
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None

    def cache_data(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Cache analysis results.

        Args:
            cache_key: Unique identifier for the cached data
            data: Data to cache
        """
        import json

        cache_file = self.cache_dir / cache_key
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except IOError:
            # Fail silently if caching fails
            pass

    def validate_stock_code(self, stock_code: str) -> bool:
        """
        Validate stock code format.

        Args:
            stock_code: Stock code to validate

        Returns:
            True if valid, False otherwise
        """
        return len(stock_code) == 6 and stock_code.isdigit()

    def calculate_score(self, metrics: Dict[str, float], thresholds: Dict[str, tuple]) -> float:
        """
        Calculate a composite score from multiple metrics.

        Args:
            metrics: Dictionary of metric names and values
            thresholds: Dictionary of metric names and (min, max, weight) tuples

        Returns:
            Composite score (0-100)
        """
        score = 0.0
        total_weight = 0.0

        for metric_name, (min_val, max_val, weight) in thresholds.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                # Normalize to 0-1 range
                if max_val > min_val:
                    normalized = (value - min_val) / (max_val - min_val)
                    normalized = max(0, min(1, normalized))  # Clamp to [0, 1]
                    score += normalized * weight
                    total_weight += weight

        if total_weight > 0:
            return (score / total_weight) * 100
        return 0.0
