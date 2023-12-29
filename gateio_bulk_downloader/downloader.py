"""
gateio_bulk_downloader
TODO: spotやその他デリバティブ指標にも対応する
"""

# import standard libraries
import os
import time
import warnings
from datetime import datetime, timedelta

import pandas as pd
# import third-party libraries
import requests
from rich import print
from rich.progress import track

# import my libraries
from gateio_bulk_downloader.exceptions import (InvalidIntervalError,
                                               InvalidSymbolFormatError)

warnings.filterwarnings("ignore")


class GateioBulkDownloader:
    _GATEIO_BASE_URL = "https://api.gateio.ws/api/v4"
    _INTERVALS_MINUTES = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "4h": 240,
        "8h": 480,
        "1d": 1440,
        "7d": 10080,
        "30d": 43200,
    }

    def __init__(
        self,
        destination_dir=".",
    ):
        """
        :param destination_dir: Directory to save the downloaded data.
        """
        self._destination_dir = destination_dir + "/gateio_data"

    def validate_symbol(self, symbol: str = "BTC_USDT") -> str:
        """
        Validate symbol format.
        :param symbol: cryptocurrency symbol.
        :return: symbol
        """
        if symbol in self.get_all_symbols_futures():
            return symbol
        else:
            raise InvalidSymbolFormatError(f"Invalid symbol: {symbol}")

    def get_all_symbols_futures(self) -> list:
        """
        Get all symbols (futures).
        :return: symbols
        """
        response = requests.get(f"{self._GATEIO_BASE_URL}/futures/usdt/contracts")
        if response.status_code == 200:
            data = response.json()
            return [i["name"] for i in data]
        else:
            print(f"[red]Error: {response.status_code}[/red]")

    def _make_url(self, symbol: str) -> str:
        """
        Make url for the request.
        :param symbol: cryptocurrency symbol.
        :return: url
        """
        return f"{self._GATEIO_BASE_URL}/futures/usdt/candlesticks"

    def _make_destination_dir(self, symbol: str = "BTC_USDT", interval: str = "1m"):
        """
        Make destination directory.
        :param symbol: cryptocurrency symbol.
        :param interval: Interval of the data.
        :return: destination_dir
        """
        return f"{self._destination_dir}/{symbol}/{interval}"

    def execute_download(
        self, symbol: str, start_date: datetime, end_date: datetime, interval: str
    ):
        """
        Execute download.
        Attention
        Return specified contract candlesticks.
        If prefix contract with mark_, the contract's mark price candlesticks are returned;
        if prefix with index_, index price candlesticks will be returned.
        Maximum of 2000 points are returned in one query.
        Be sure not to exceed the limit when specifying from, to and interval
        :param symbol: cryptocurrency symbol.
        :param start_date: Start date of the data.
        :param end_date: End date of the data.
        :param interval: Interval of the data.
        """
        max_retries = 5  # Maximum number of retries
        retry_delay = 30  # Seconds to wait before retrying (30 seconds)

        params = {
            "contract": self.validate_symbol(symbol),
            "from": int(start_date.timestamp()),
            "to": int(end_date.timestamp()),
            "interval": interval,
        }
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    self._make_url(symbol), params=params, headers=headers
                )
                print(
                    f"[green]Success: {self._make_destination_dir(symbol, interval)}/{int(start_date.timestamp())}.csv[/green]"
                )
                if response.status_code == 200:
                    data = response.json()
                    if data == []:
                        print(f"[yellow]Skip: {symbol}[/yellow]")
                        break
                    df = pd.DataFrame(data)
                    df["t"] = pd.to_datetime(df["t"], unit="s")
                    df.to_csv(
                        f"{self._make_destination_dir(symbol, interval)}/{int(start_date.timestamp())}.csv",
                        index=False,
                    )
                else:
                    print(f"[red]Error: {response.status_code}[/red]")
                break
            except (requests.ConnectionError, requests.HTTPError) as e:
                print(f"[red]Error: {e}[/red]")
                time.sleep(retry_delay)
                attempt += 1
        else:
            print(f"[red]Error: Failed to download[/red]")

    def download(
        self,
        symbol: str,
        start_date: datetime = None,
        end_date: datetime = None,
        interval: str = "1m",
    ):
        """
        Download data.
        :param symbol: cryptocurrency symbol.
        :param start_date: Start date of the data.
        :param end_date: End date of the data.
        :param interval: Interval of the data.
        """
        self.validate_symbol(symbol)

        if not os.path.exists(self._make_destination_dir(symbol, interval)):
            os.makedirs(self._make_destination_dir(symbol, interval))

        # 全てのデータを取得する場合
        if start_date is None and end_date is None:
            init_start_date = datetime(2020, 1, 1)
            init_end_date = datetime.now()
            # 2000分ずつデータを取得する
            while True:
                step_time = 2000 * self._INTERVALS_MINUTES[interval]
                # 2秒で20回までの制限があるので、それを考慮する
                if init_start_date + timedelta(minutes=step_time) < init_end_date:
                    # 存在確認
                    if os.path.exists(
                        f"{self._make_destination_dir(symbol, interval)}/{int(init_start_date.timestamp())}.csv"
                    ):
                        print(
                            f"[yellow]Skip: {self._make_destination_dir(symbol, interval)}/{int(init_start_date.timestamp())}.csv[/yellow]"
                        )
                        init_start_date = init_start_date + timedelta(minutes=step_time)
                        continue
                    self.execute_download(
                        symbol,
                        init_start_date,
                        init_start_date + timedelta(minutes=step_time),
                        interval,
                    )
                    init_start_date = init_start_date + timedelta(minutes=step_time)
                    time.sleep(0.1)
                else:
                    self.execute_download(
                        symbol, init_start_date, init_end_date, interval
                    )
                    break

        # all.csvが1日以内に作成されている場合はpassする
        # そうでない場合は削除して作り直す
        if os.path.exists(f"{self._make_destination_dir(symbol, interval)}/all.csv"):
            if datetime.fromtimestamp(
                os.path.getmtime(
                    f"{self._make_destination_dir(symbol, interval)}/all.csv"
                )
            ) > datetime.now() - timedelta(days=1):
                print(
                    f"[yellow]Skip: {self._make_destination_dir(symbol, interval)}/all.csv[/yellow]"
                )
                return
            else:
                os.remove(f"{self._make_destination_dir(symbol, interval)}/all.csv")

        # データを結合する
        df = pd.DataFrame()
        for file in os.listdir(self._make_destination_dir(symbol, interval)):
            print(f"[green]Concat: {file}[/green]")
            df = pd.concat(
                [
                    df,
                    pd.read_csv(
                        f"{self._make_destination_dir(symbol, interval)}/{file}"
                    ),
                ]
            )
        # 時間でソートする
        df.sort_values(by="t", inplace=True)

        # ヘッダーを設定
        df.to_csv(
            f"{self._make_destination_dir(symbol, interval)}/all.csv", index=False
        )

    def download_all(self, interval: str = "1m"):
        """
        Download all data.
        :param interval: Interval of the data.
        """
        for symbol in track(
            self.get_all_symbols_futures(),
            description="Downloading...",
            total=len(self.get_all_symbols_futures()),
        ):
            print(f"[green]Downloading: {symbol}[/green]")
            self.download(symbol, None, None, interval)
