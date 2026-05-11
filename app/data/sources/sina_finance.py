"""
Sina Finance news client for macro and industry news.

Sina Finance is a major Chinese financial news source that provides
comprehensive coverage of policy, market news, and sector updates.
Unlike some sources, it's more accessible for data collection.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import settings


class SinaFinanceClient:
    """Client for Sina Finance news."""

    def __init__(self):
        """Initialize Sina Finance client."""
        self.rate_limit = settings.caixin_rate_limit
        self.cache_dir = settings.cache_path

        # Sina Finance URLs
        self.base_url = "https://finance.sina.com.cn"
        self.roll_url = f"{self.base_url}/roll/"
        self.sina_finance_url = f"{self.base_url}/"

        # News section URLs by sector
        self.sector_urls = {
            "AI": f"{self.base_url}/tech/",
            "Robotics": f"{self.base_url}/tech/",
            "Military": f"{self.base_url}/roll/",
            "Energy": f"{self.base_url}/energy/",
            "Biopharma": f"{self.base_url}/finance/",
        }

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_macro_news(self, days: int = 7) -> List[Dict]:
        """
        Get macro-economic and policy news from Sina Finance.

        Args:
            days: Number of days to look back

        Returns:
            List of news article dictionaries
        """
        # Check cache first
        cache_key = f"sina_macro_news_{days}"
        cached = self._get_cache(cache_key, max_age_hours=4)
        if cached:
            return cached

        try:
            print(f"Fetching macro news from Sina Finance...")

            # Fetch from roll page (rolling news)
            response = requests.get(self.roll_url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            news_list = []
            cutoff_date = datetime.now() - timedelta(days=days)

            # Try different selectors to find news items
            news_items = (
                soup.select("li")
                + soup.select("div[class*='item']")
                + soup.select("a[href*='sina.com.cn']")
            )

            for item in news_items:
                try:
                    # Find title link
                    link_elem = item.find("a")
                    if not link_elem:
                        continue

                    title = link_elem.get_text(strip=True)
                    url = link_elem.get("href", "")

                    if not url.startswith("http"):
                        if url.startswith("/"):
                            url = f"{self.base_url}{url}"
                        else:
                            url = f"{self.base_url}/{url}"

                    # Try to extract date
                    date_elem = item.find("span", class_="date") or item.find("time")
                    if date_elem:
                        date_text = date_elem.get_text(strip=True)
                        news_date = self._parse_date(date_text)
                    else:
                        news_date = datetime.now()

                    # Skip if too old
                    if news_date < cutoff_date:
                        continue

                    # Skip if already have this URL
                    if any(news["url"] == url for news in news_list):
                        continue

                    # Fetch article content if not too many
                    if len(news_list) < 15:
                        content = self._fetch_article_content(url)
                    else:
                        content = ""

                    # Analyze sentiment
                    sentiment = self.analyze_sentiment(title + " " + content)

                    news_list.append({
                        "title": title,
                        "content": content[:500] if content else "",  # Limit content length
                        "date": news_date.strftime("%Y-%m-%d"),
                        "source": "新浪财经",
                        "url": url,
                        "sentiment": sentiment,
                    })

                    # Limit to 20 articles
                    if len(news_list) >= 20:
                        break

                except Exception as e:
                    print(f"Error parsing news item: {e}")
                    continue

            # Cache the result
            self._save_cache(cache_key, news_list)

            print(f"✓ Fetched {len(news_list)} news articles from Sina Finance")
            return news_list

        except Exception as e:
            print(f"Error fetching macro news from Sina Finance: {e}")
            return []

    def get_industry_news(self, industry: str, days: int = 7) -> List[Dict]:
        """
        Get industry-specific news from Sina Finance.

        Args:
            industry: Industry name
            days: Number of days to look back

        Returns:
            List of news article dictionaries
        """
        # Get all macro news and filter by industry keywords
        all_news = self.get_macro_news(days)

        # Industry keywords for filtering
        industry_keywords = {
            "AI": ["人工智能", "AI", "机器学习", "深度学习", "大模型", "算法", "智能"],
            "Robotics": ["机器人", "智能制造", "工业机器人", "自动化", "机械", "装备"],
            "Military Industry": ["军工", "国防", "航空", "船舶", "导弹", "军工电子", "航天"],
            "Electricity & New Energy": ["新能源", "光伏", "风电", "电池", "电动车", "充电桩", "锂电", "太阳能"],
            "Biopharma": ["医药", "生物制药", "疫苗", "新药", "仿制药", "创新药", "医疗"],
        }

        keywords = industry_keywords.get(industry, [])

        if not keywords:
            return []

        # Filter news by industry keywords
        filtered_news = []
        for news in all_news:
            content = (news.get('title', '') + ' ' + news.get('content', '')).lower()

            # Check if any keyword matches
            if any(keyword.lower() in content for keyword in keywords):
                filtered_news.append(news)

        print(f"✓ Filtered {len(filtered_news)} {industry} news articles")

        return filtered_news

    def _fetch_article_content(self, url: str) -> str:
        """
        Fetch content of a specific article.

        Args:
            url: Article URL

        Returns:
            Article content text
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Try to find article content
            content_div = (
                soup.find("div", class_="article")
                or soup.find("div", class_="content")
                or soup.find("article")
                or soup.find("div", id="article-content")
            )

            if content_div:
                content = content_div.get_text(strip=True)
                return content

            return ""

        except Exception as e:
            print(f"Error fetching article content from {url}: {e}")
            return ""

    def _parse_date(self, date_text: str) -> datetime:
        """
        Parse date string to datetime.

        Args:
            date_text: Date string

        Returns:
            Datetime object
        """
        import re

        # Try different date formats
        formats = [
            "%Y-%m-%d %H:%M",
            "%Y年%m月%d日",
            "%Y-%m-%d",
            "%m/%d %H:%M",
            "%H:%M",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_text, fmt)
            except ValueError:
                continue

        # Default to now if parsing fails
        return datetime.now()

    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of news text.

        TODO: Implement proper NLP sentiment analysis.
        Options for future development:
        1. Chinese NLP Library (e.g., SnowNLP, jieba + sentiment models)
        2. Commercial API (e.g., Baidu Sentiment Analysis API)
        3. Transformer Models (e.g., BERT fine-tuned for Chinese)

        Args:
            text: Text to analyze

        Returns:
            Sentiment score (-1.0 to 1.0)
        """
        # Placeholder for future development
        return 0.0

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
