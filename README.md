# gateio-bulk-downloader

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110//)


## Python library for bulk downloading Gate.io historical data
A Python library to efficiently and concurrently download historical data files from Gateio. Supports USDT Perpetual.

## Installation

```bash
pip install git+https://github.com/aoki-h-jp/gateio-bulk-downloader
```

## Usage
### Download all kline data (USDT Perpetual)

```python
from gateio_bulk_downloader.downloader import GateioBulkDownloader

downloader = GateioBulkDownloader(destination_dir=".")
downloader.download_all()
```

## pytest
Work in progress.

## If you want to report a bug or request a feature
Please create an issue on this repository!

## Disclaimer
This project is for educational purposes only. You should not construe any such information or other material as legal,
tax, investment, financial, or other advice. Nothing contained here constitutes a solicitation, recommendation,
endorsement, or offer by me or any third party service provider to buy or sell any securities or other financial
instruments in this or in any other jurisdiction in which such solicitation or offer would be unlawful under the
securities laws of such jurisdiction.

Under no circumstances will I be held responsible or liable in any way for any claims, damages, losses, expenses, costs,
or liabilities whatsoever, including, without limitation, any direct or indirect damages for loss of profits.
r