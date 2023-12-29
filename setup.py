from setuptools import setup

setup(
    name="gateio-bulk-downloader",
    version="1.0.0",
    description="Python library to efficiently and concurrently download historical data files from Gateio. Supports all asset types (spot, USDT-M) and all data frequencies.",
    install_requires=[
        "requests",
        "rich",
        "pytest",
        "pandas",
    ],
    author="aoki-h-jp",
    author_email="aoki.hirotaka.biz@gmail.com",
    license="MIT",
    packages=["gateio_bulk_downloader"],
)
