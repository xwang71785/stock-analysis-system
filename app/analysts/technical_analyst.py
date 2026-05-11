"""
Technical analyst for the Stock Analysis System.

This module performs technical analysis of stocks based on price data,
technical indicators, and chart patterns.
"""
from typing import Any, Dict, List, Optional

import numpy as np

from app.analysts.base_analyst import BaseAnalyst
from app.data.models import TechnicalAnalysis, TechnicalIndicator, TradingPattern
from app.data.sources.tushare_client import TushareClient


class TechnicalAnalyst(BaseAnalyst):
    """Analyst for technical stock analysis."""

    def __init__(self, stock_code: str):
        """
        Initialize the technical analyst.

        Args:
            stock_code: The stock code to analyze
        """
        super().__init__(stock_code)
        self.tushare_client = TushareClient()

    def analyze(self) -> Dict[str, Any]:
        """
        Perform technical analysis.

        Returns:
            Dictionary containing technical analysis results
        """
        try:
            # Fetch price data (last 3 months)
            price_data = self.tushare_client.get_daily_prices(self.stock_code)

            if not price_data or len(price_data) < 60:
                return {
                    "error": "Insufficient price data for technical analysis",
                    "stock_code": self.stock_code,
                }

            # Convert to numpy arrays for calculation
            closes = np.array([p["close"] for p in price_data])
            highs = np.array([p["high"] for p in price_data])
            lows = np.array([p["low"] for p in price_data])
            volumes = np.array([p.get("vol", 0) for p in price_data])

            # Calculate technical indicators
            indicators = self._calculate_indicators(closes, highs, lows)

            # Detect patterns
            pattern = self._detect_patterns(closes, highs, lows, volumes)

            # Identify support and resistance
            key_levels = self._identify_support_resistance(closes)

            # Generate trading signal
            signal, confidence = self._generate_signal(indicators, pattern)

            # Determine failure conditions
            failure_conditions = self._determine_failure_conditions(closes, key_levels)

            return {
                "signal": signal,
                "confidence": confidence,
                "key_levels": key_levels,
                "current_pattern": pattern.model_dump() if pattern else None,
                "indicators": indicators.model_dump(),
                "failure_conditions": failure_conditions,
            }

        except Exception as e:
            return {
                "error": f"Technical analysis failed: {str(e)}",
                "stock_code": self.stock_code,
            }

    def _calculate_indicators(
        self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray
    ) -> TechnicalIndicator:
        """
        Calculate technical indicators.

        Args:
            closes: Array of close prices
            highs: Array of high prices
            lows: Array of low prices

        Returns:
            TechnicalIndicator object with calculated values
        """
        # Moving Averages
        ma_5 = self._calculate_ma(closes, 5)
        ma_10 = self._calculate_ma(closes, 10)
        ma_20 = self._calculate_ma(closes, 20)
        ma_60 = self._calculate_ma(closes, 60)

        # MACD
        macd, macd_signal, macd_hist = self._calculate_macd(closes)

        # RSI
        rsi = self._calculate_rsi(closes)

        # KDJ
        kdj_k, kdj_d, kdj_j = self._calculate_kdj(highs, lows, closes)

        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(closes)

        return TechnicalIndicator(
            ma_5=float(ma_5[-1]),
            ma_10=float(ma_10[-1]),
            ma_20=float(ma_20[-1]),
            ma_60=float(ma_60[-1]),
            macd=float(macd[-1]),
            macd_signal=float(macd_signal[-1]),
            macd_hist=float(macd_hist[-1]),
            rsi=float(rsi[-1]),
            kdj_k=float(kdj_k[-1]),
            kdj_d=float(kdj_d[-1]),
            kdj_j=float(kdj_j[-1]),
            bb_upper=float(bb_upper[-1]),
            bb_middle=float(bb_middle[-1]),
            bb_lower=float(bb_lower[-1]),
        )

    def _calculate_ma(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Simple Moving Average."""
        return np.convolve(data, np.ones(period) / period, mode="valid")

    def _calculate_macd(self, prices: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate MACD indicator."""
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd = ema_12 - ema_26
        signal = self._calculate_ema(macd, 9)
        hist = macd - signal
        return macd, signal, hist

    def _calculate_ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average."""
        multiplier = 2 / (period + 1)
        ema = np.zeros_like(data)
        ema[0] = data[0]

        for i in range(1, len(data)):
            ema[i] = (data[i] - ema[i - 1]) * multiplier + ema[i - 1]

        return ema

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate RSI indicator."""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gains = np.convolve(gains, np.ones(period) / period, mode="valid")
        avg_losses = np.convolve(losses, np.ones(period) / period, mode="valid")

        rs = np.divide(avg_gains, avg_losses, where=avg_losses != 0)
        rsi = 100 - (100 / (1 + rs))

        # Pad with initial values
        rsi = np.concatenate([np.full(period - 1, 50), rsi])

        return rsi

    def _calculate_kdj(
        self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 9
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate KDJ indicator."""
        n = period
        lowest_low = np.convolve(lows, np.ones(n) / n, mode="valid")
        highest_high = np.convolve(highs, np.ones(n) / n, mode="valid")

        rsv = 100 * (closes[n - 1 :] - lowest_low) / (highest_high - lowest_low)

        k = np.full(len(closes), 50.0)
        d = np.full(len(closes), 50.0)
        j = np.full(len(closes), 50.0)

        for i in range(n - 1, len(closes)):
            idx = i - (n - 1)
            k[i] = (2 / 3) * k[i - 1] + (1 / 3) * rsv[idx]
            d[i] = (2 / 3) * d[i - 1] + (1 / 3) * k[i]
            j[i] = 3 * k[i] - 2 * d[i]

        return k, d, j

    def _calculate_bollinger_bands(
        self, prices: np.ndarray, period: int = 20, std_dev: float = 2.0
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate Bollinger Bands."""
        ma = np.convolve(prices, np.ones(period) / period, mode="valid")
        std = np.array([np.std(prices[i - period + 1 : i + 1]) for i in range(period - 1, len(prices))])

        upper = ma + std_dev * std
        lower = ma - std_dev * std

        # Pad with initial values
        upper = np.concatenate([np.full(period - 1, ma[0]), upper])
        middle = np.concatenate([np.full(period - 1, ma[0]), ma])
        lower = np.concatenate([np.full(period - 1, ma[0]), lower])

        return upper, middle, lower

    def _detect_patterns(
        self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray, volumes: np.ndarray
    ) -> Optional[TradingPattern]:
        """
        Detect trading patterns in price data.

        Args:
            closes: Array of close prices
            highs: Array of high prices
            lows: Array of low prices
            volumes: Array of volumes

        Returns:
            TradingPattern object if pattern detected, None otherwise
        """
        # This is a simplified pattern detection
        # In production, you'd use more sophisticated algorithms

        recent_closes = closes[-20:]

        # Check for double bottom
        if self._is_double_bottom(recent_closes):
            return TradingPattern(
                pattern_name="double_bottom",
                pattern_type="reversal",
                confidence=0.7,
                description="Price formed two bottoms at similar levels, indicating potential reversal",
            )

        # Check for breakout
        if self._is_breakout(recent_closes):
            return TradingPattern(
                pattern_name="breakout",
                pattern_type="continuation",
                confidence=0.8,
                description="Price broke above resistance level with strong volume",
            )

        # Check for consolidation
        if self._is_consolidation(recent_closes):
            return TradingPattern(
                pattern_name="consolidation",
                pattern_type="neutral",
                confidence=0.6,
                description="Price is trading in a range, waiting for direction",
            )

        return None

    def _is_double_bottom(self, prices: np.ndarray) -> bool:
        """Check for double bottom pattern."""
        if len(prices) < 10:
            return False

        # Find local minima
        min_val = np.min(prices)
        min_indices = np.where(prices == min_val)[0]

        if len(min_indices) >= 2:
            # Check if there are two distinct minima
            return min_indices[-1] - min_indices[0] >= 5

        return False

    def _is_breakout(self, prices: np.ndarray) -> bool:
        """Check for breakout pattern."""
        if len(prices) < 10:
            return False

        # Check if recent price is significantly higher than recent range
        recent_range = np.max(prices[:-5]) - np.min(prices[:-5])
        if recent_range == 0:
            return False

        current_price = prices[-1]
        avg_price = np.mean(prices[:-5])

        return current_price > avg_price + 0.5 * recent_range

    def _is_consolidation(self, prices: np.ndarray) -> bool:
        """Check for consolidation pattern."""
        if len(prices) < 10:
            return False

        price_range = np.max(prices) - np.min(prices)
        avg_price = np.mean(prices)

        # If price range is small relative to average price
        return price_range / avg_price < 0.05  # Less than 5% variation

    def _identify_support_resistance(self, closes: np.ndarray) -> Dict[str, float]:
        """
        Identify key support and resistance levels.

        Args:
            closes: Array of close prices

        Returns:
            Dictionary with support and resistance levels
        """
        recent_prices = closes[-30:]

        # Simple approach: use recent minima and maxima
        support = float(np.min(recent_prices))
        resistance = float(np.max(recent_prices))

        return {
            "support": support,
            "resistance": resistance,
            "current": float(closes[-1]),
        }

    def _generate_signal(
        self, indicators: TechnicalIndicator, pattern: Optional[TradingPattern]
    ) -> tuple[str, str]:
        """
        Generate trading signal based on indicators and patterns.

        Args:
            indicators: Calculated technical indicators
            pattern: Detected trading pattern

        Returns:
            Tuple of (signal, confidence)
        """
        buy_signals = 0
        sell_signals = 0
        total_signals = 0

        # Moving average signals
        if indicators.ma_5 > indicators.ma_10:
            buy_signals += 1
        else:
            sell_signals += 1
        total_signals += 1

        if indicators.ma_10 > indicators.ma_20:
            buy_signals += 1
        else:
            sell_signals += 1
        total_signals += 1

        # MACD signal
        if indicators.macd > indicators.macd_signal:
            buy_signals += 1
        else:
            sell_signals += 1
        total_signals += 1

        # RSI signal
        if indicators.rsi < 30:
            buy_signals += 2  # Strong buy signal
        elif indicators.rsi > 70:
            sell_signals += 2  # Strong sell signal
        elif indicators.rsi < 40:
            buy_signals += 1
        elif indicators.rsi > 60:
            sell_signals += 1
        total_signals += 2

        # KDJ signal
        if indicators.kdj_k < 20:
            buy_signals += 1
        elif indicators.kdj_k > 80:
            sell_signals += 1
        total_signals += 1

        # Pattern override
        if pattern:
            if pattern.pattern_type == "reversal" and pattern.confidence > 0.7:
                # Pattern is strong reversal
                if pattern.pattern_name == "double_bottom":
                    buy_signals += 2
                elif pattern.pattern_name == "double_top":
                    sell_signals += 2

        # Determine signal and confidence
        net_signal = buy_signals - sell_signals
        max_signal = total_signals

        if net_signal >= max_signal * 0.5:
            signal = "buy"
            confidence = "high" if net_signal >= max_signal * 0.75 else "medium"
        elif net_signal <= -max_signal * 0.5:
            signal = "sell"
            confidence = "high if" " net_signal <= -max_signal * 0.75 else medium"
        else:
            signal = "watch"
            confidence = "medium"

        return signal, confidence

    def _determine_failure_conditions(self, closes: np.ndarray, key_levels: Dict[str, float]) -> List[str]:
        """
        Determine conditions that would invalidate the trading signal.

        Args:
            closes: Array of close prices
            key_levels: Support and resistance levels

        Returns:
            List of failure conditions
        """
        conditions = []

        support = key_levels.get("support", 0)
        resistance = key_levels.get("resistance", 0)
        current = float(closes[-1])

        # Distance to support and resistance
        if support > 0:
            support_distance = (current - support) / support
            if support_distance < 0.02:  # Within 2% of support
                conditions.append(f"Close below support level at {support:.2f}")

        if resistance > 0:
            resistance_distance = (resistance - current) / current
            if resistance_distance < 0.02:  # Within 2% of resistance
                conditions.append(f"Close above resistance level at {resistance:.2f}")

        return conditions if conditions else ["No specific failure conditions"]
