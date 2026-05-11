"""
Caixin news scraper for macro policy and financial news.

This module provides scraping functionality for Caixin's finance and policy sections.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import settings


class CaixinScraper:
    """Scraper for Caixin news articles."""

    def __init__(self):
        """Initialize Caixin scraper."""
        self.rate_limit = settings.caixin_rate_limit
        self.cache_dir = settings.cache_path
        self.last_request_time = 0

        # Caixin URLs
        self.base_url = "https://economy.caixin.com"
        self.finance_url = f"{self.base_url}/"
        self.macro_url = f"{self.base_url}/"

        # User agent to avoid blocking
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_macro_news(self, days: int = 7) -> List[Dict]:
        """
        Get macro-economic and policy news from Caixin.

        Args:
            days: Number of days to look back

        Returns:
            List of news article dictionaries
        """
        # Check cache first
        cache_key = f"caixin_macro_news_{days}"
        cached = self._get_cache(cache_key, max_age_hours=4)
        if cached:
            return cached

        try:
            # Fetch the macro news page
            url = f"{self.macro_url}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Parse news articles (adjust selectors based on actual page structure)
            news_items = []

            # Find article links (this is a generic approach - actual selectors may vary)
            article_links = soup.find_all("a", class_="news-title") or soup.find_all("h3") or soup.find_all("h4")

            cutoff_date = datetime.now() - timedelta(days=days)

            for link in article_links:
                try:
                    # Get article URL
                    article_url = link.get("href")
                    if not article_url or not article_url.startswith("http"):
                        continue

                    # Make URL absolute if needed
                    if article_url.startswith("/"):
                        article_url = f"{self.base_url}{article_url}"

                    # Fetch article details
                    article_data = self._fetch_article(article_url)

                    if article_data:
                        # Check if article is within date range
                        article_date = datetime.strptime(article_data["date"], "%Y-%m-%d")
                        if article_date >= cutoff_date:
                            news_items.append(article_data)

                            # Limit to 20 articles
                            if len(news_items) >= 20:
                                break

                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue

            # Cache the result
            self._save_cache(cache_key, news_items)

            return news_items

        except Exception as e:
            print(f"Error fetching macro news: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_industry_news(self, industry: str, days: int = 7) -> List[Dict]:
        """
        Get industry-specific news from Caixin.

        Args:
            industry: Industry to search for
            days: Number of days to look back

        Returns:
            List of news article dictionaries
        """
        # Check cache first
        cache_key = f"caixin_industry_news_{industry}_{days}"
        cached = self._get_cache(cache_key, max_age_hours=4)
        if cached:
            return cached

        try:
            # This is a placeholder - actual implementation would need to
            # search for industry-specific news on Caixin
            # For now, return macro news as a fallback
            return self.get_macro_news(days=days)

        except Exception as e:
            print(f"Error fetching industry news for {industry}: {e}")
            return []

    def _fetch_article(self, url: str) -> Optional[Dict]:
        """
        Fetch and parse a single article.

        Args:
            url: Article URL

        Returns:
            Dictionary with article data or None
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract article data
            title = soup.find("h1") or soup.find("title")
            title = title.get_text(strip=True) if title else "Untitled"

            # Find article content
            content = soup.find("div", class_="article-content") or soup.find("article")
            if content:
                content = content.get_text(strip=True)
            else:
                content = ""

            # Find publication date
            date_element = soup.find("time") or soup.find("span", class_="date")
            if date_element:
                date_text = date_element.get_text(strip=True)
                # Try to parse date
                try:
                    date = datetime.strptime(date_text.split()[0], "%Y-%m-%d")
                except ValueError:
                    date = datetime.now()
            else:
                date = datetime.now()

            return {
                "title": title,
                "content": content[:1000],  # Limit content length
                "date": date.strftime("%Y-%m-%d"),
                "source": "Caixin",
                "url": url,
            }

        except Exception as e:
            print(f"Error fetching article from {url}: {e}")
            return None

    def analyze_sentiment(self, text: str) -> float:
        """
        Simple sentiment analysis for news text.

        Args:
            text: Text to analyze

        Returns:
            Sentiment score (-1.0 to 1.0)
        """
        # This is a simple keyword-based approach
        # In production, you'd want to use a proper NLP library
        positive_keywords = [
            "growth",
            "increase",
            "profit",
            "expansion",
            "improvement",
            "upgrade",
            "positive",
            "strong",
            "boost",
            "gain",
            "上涨",
            "增长",
            "利好",
            "突破",
            "强劲",
            "提升",
        ]

        negative_keywords = [
            "decline",
            "decrease",
            "loss",
            "recession",
            "downturn",
            "negative",
            "weak",
            "cut",
            "drop",
            "下跌",
            "下降",
            "利空",
            "衰退",
            "疲软",
            "削减",
        ]

        text_lower = text.lower()

        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)

        total = positive_count + negative_count
        if total == 0:
            return 0.0

        return (positive_count - negative_count) / total

    def _get_cache(self, key: str, max_age_hours: int = 4) -> Optional[List[Dict]]:
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

    def _save_cache(self, key: str, data: List[Dict]) -> None:
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
