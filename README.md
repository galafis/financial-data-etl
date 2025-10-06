# 🔄 Financial Data ETL Pipeline

[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.2-green.svg)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Complete ETL (Extract, Transform, Load) pipeline for financial market data with data quality validation and technical indicators.

## Features

- **Multiple Sources**: CSV, JSON, API extraction
- **Data Validation**: OHLC validation, duplicate removal, missing value handling
- **Technical Indicators**: SMA, RSI, volatility, returns
- **Resampling**: Convert to different timeframes (daily → weekly, etc.)
- **Quality Reports**: Comprehensive data quality tracking
- **Multiple Formats**: Output to Parquet, CSV, JSON

## Quick Start

```python
from etl_pipeline import FinancialDataETL

etl = FinancialDataETL(output_format='parquet')

df = etl.run_pipeline(
    source_type='api',
    source_path='BTCUSD',
    output_path='data/btcusd.parquet',
    add_indicators=True,
    resample_freq='W'
)
```

## Author

**Gabriel Demetrios Lafis**
