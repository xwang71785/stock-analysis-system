"""
CNINFO Annual Report Downloader

Downloads annual reports from cninfo.com.cn for specified stocks.
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlencode

import httpx


class CNINFODownloader:
    """Client for downloading annual reports from cninfo.com.cn."""

    def __init__(self, download_dir: str = "reports"):
        """Initialize CNINFO downloader.

        Args:
            download_dir: Directory to save downloaded reports
        """
        self.base_url = "http://www.cninfo.com.cn"
        self.api_url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "http://www.cninfo.com.cn/new/disclosure/stock",
        }

    def search_annual_reports(
        self,
        stock_code: str,
        stock_name: str,
        years: int = 3
    ) -> List[Dict]:
        """Search for annual reports of a stock.

        Args:
            stock_code: Stock code (e.g., '000977')
            stock_name: Stock name (e.g., '浪潮信息')
            years: Number of recent years to fetch

        Returns:
            List of annual report metadata
        """
        # Determine exchange
        column = "szse"  # Shenzhen Stock Exchange
        if stock_code.startswith("6"):
            column = "sse"  # Shanghai Stock Exchange

        # Search for "公司名 年度报告" to get annual reports
        search_key = f"{stock_name} 年度报告"

        params = {
            "searchkey": search_key,
            "stock": "",
            "plate": "",
            "category": "",
            "trade": "",
            "column": column,
            "columnTitle": "历史公告查询",
            "pageNum": "1",
            "pageSize": "100",
            "tabName": "fulltext",
            "sortName": "",
            "sortType": "",
            "limit": "",
            "showTitle": "",
            "seDate": "",
        }

        all_annual_reports = []

        try:
            with httpx.Client(headers=self.headers, timeout=30.0) as client:
                response = client.post(self.api_url, data=params)
                response.raise_for_status()
                data = response.json()

            records = data.get("announcements", [])

            # Filter for annual reports (exclude summaries and semi-annual reports)
            annual_keywords = ["年度报告"]
            exclude_keywords = ["摘要", "半年度", "中期"]

            for record in records:
                # Check if it's for the correct stock code
                sec_code = record.get("secCode", "")
                if sec_code != stock_code:
                    continue

                title = record.get("announcementTitle", "")
                # Check if it's an annual report
                if any(kw in title for kw in annual_keywords):
                    # Exclude summaries and semi-annual reports
                    if not any(excl in title for excl in exclude_keywords):
                        # Avoid duplicates
                        announcement_id = record.get("announcementId")
                        if not any(r.get("announcement_id") == announcement_id for r in all_annual_reports):
                            all_annual_reports.append({
                                "title": title,
                                "announcement_id": announcement_id,
                                "adjunct_url": record.get("adjunctUrl"),
                                "adjunct_size": record.get("adjunctSize"),
                                "publish_time": record.get("announcementTime"),
                                "stock_code": stock_code,
                                "stock_name": stock_name,
                            })

        except Exception as e:
            print(f"Error searching annual reports for {stock_code}: {e}")
            return []

        # Sort by publish time (newest first) - announcementTime is timestamp in ms
        all_annual_reports.sort(key=lambda x: int(x["publish_time"] or 0), reverse=True)

        # Limit to specified number of years
        if all_annual_reports and years:
            all_annual_reports = all_annual_reports[:years]

        return all_annual_reports

    def download_report(self, report: Dict) -> Optional[str]:
        """Download a single annual report.

        Args:
            report: Report metadata dictionary

        Returns:
            Path to downloaded file or None if failed
        """
        adjunct_url = report.get("adjunct_url")
        if not adjunct_url:
            print(f"No download URL for report: {report['title']}")
            return None

        # Construct full download URL - use static.cninfo.com.cn for downloads
        download_url = adjunct_url
        if not download_url.startswith("http"):
            # CNINFO stores files on static.cninfo.com.cn
            if not download_url.startswith("/"):
                download_url = "/" + download_url
            download_url = f"http://static.cninfo.com.cn{download_url}"

        # Create filename
        stock_code = report["stock_code"]
        stock_name = report["stock_name"]

        # Convert timestamp to readable format
        publish_time = report.get("publish_time")
        if publish_time:
            try:
                # Convert milliseconds timestamp to datetime string
                timestamp_ms = int(publish_time)
                from datetime import datetime
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                publish_time = dt.strftime("%Y%m%d")
            except (ValueError, TypeError):
                publish_time = str(publish_time)
        else:
            publish_time = "unknown"

        # Use part of title to make filename unique
        title = report["title"].replace("/", "_").replace("\\", "_")
        # Extract key words from title for uniqueness
        title_suffix = title[:30] if "年度报告" not in title else "年度报告"
        if "摘要" in title:
            title_suffix = "摘要"
        elif "提示性公告" in title:
            title_suffix = "提示性公告"
        elif "制度" in title:
            title_suffix = "制度"

        # Extract file extension from URL
        ext = ".pdf"
        if ".PDF" in download_url.upper():
            ext = ".pdf"

        filename = f"{stock_code}_{stock_name}_{publish_time}_{title_suffix}{ext}"
        filepath = self.download_dir / filename

        # Handle duplicate filenames by adding counter
        counter = 1
        while filepath.exists():
            base = filepath.stem
            filename = f"{base}_{counter}{ext}"
            filepath = self.download_dir / filename
            counter += 1

        try:
            with httpx.Client(headers=self.headers, timeout=60.0, follow_redirects=True) as client:
                response = client.get(download_url)
                response.raise_for_status()

            with open(filepath, "wb") as f:
                f.write(response.content)

            print(f"Downloaded: {filename} ({len(response.content) / 1024 / 1024:.2f} MB)")
            return str(filepath)

        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            return None

    def download_stock_reports(
        self,
        stock_code: str,
        stock_name: str,
        years: int = 3
    ) -> List[str]:
        """Download all annual reports for a stock.

        Args:
            stock_code: Stock code
            stock_name: Stock name
            years: Number of recent years to download

        Returns:
            List of downloaded file paths
        """
        print(f"\nSearching annual reports for {stock_name} ({stock_code})...")
        reports = self.search_annual_reports(stock_code, stock_name, years)

        if not reports:
            print(f"No annual reports found for {stock_name} ({stock_code})")
            return []

        print(f"Found {len(reports)} annual report(s)")
        for i, report in enumerate(reports, 1):
            print(f"  {i}. {report['title']} - {report['publish_time']}")

        downloaded_files = []
        for report in reports:
            filepath = self.download_report(report)
            if filepath:
                downloaded_files.append(filepath)
            time.sleep(1)  # Be polite to the server

        print(f"\nDownloaded {len(downloaded_files)} file(s)")
        return downloaded_files


def load_stock_list(filepath: str) -> Dict:
    """Load stock list from JSON file.

    Args:
        filepath: Path to stock_list.json

    Returns:
        Dictionary containing stock data
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """Main function to download annual report for the first stock."""
    # Load stock list
    stock_list_path = Path("stock_list.json")
    if not stock_list_path.exists():
        print(f"Error: {stock_list_path} not found")
        return

    stock_data = load_stock_list(stock_list_path)

    # Get first stock
    stocks = stock_data.get("stocks", [])
    if not stocks:
        print("No stocks found in stock_list.json")
        return

    first_stock = stocks[7]
    stock_code = first_stock["code"]
    stock_name = first_stock["name"]

    print(f"Downloading annual reports for: {stock_name} ({stock_code})")

    # Create downloader and download reports
    downloader = CNINFODownloader(download_dir="reports")
    downloaded_files = downloader.download_stock_reports(stock_code, stock_name, years=3)

    if downloaded_files:
        print("\nDownloaded files:")
        for filepath in downloaded_files:
            print(f"  - {filepath}")
    else:
        print("\nNo files were downloaded")


if __name__ == "__main__":
    main()
