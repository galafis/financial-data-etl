# 🔄 Financial Data ETL Pipeline


[English](#english) | [Português](#português)

---

## English

### Overview

Production-ready ETL (Extract, Transform, Load) pipeline for financial market data with comprehensive data quality validation, technical indicators calculation, and multi-format support. Designed for quantitative trading platforms and financial data warehouses.

### Key Features

- **Multiple Data Sources**: CSV, JSON, REST API extraction
- **Data Validation**: OHLC integrity checks, duplicate removal, missing value handling
- **Technical Indicators**: SMA, RSI, volatility, returns, momentum
- **Time Resampling**: Convert between timeframes (tick → minute → hour → daily → weekly)
- **Quality Reports**: Detailed data quality tracking and issue logging
- **Multiple Output Formats**: Parquet, CSV, JSON with compression
- **Error Handling**: Comprehensive error recovery and logging
- **Scalability**: Efficient processing of large datasets with pandas

### Architecture

```
┌─────────────────────────────────────────┐
│         Data Sources                    │
│  ┌─────────┬─────────┬──────────────┐  │
│  │   CSV   │  JSON   │  REST API    │  │
│  └────┬────┴────┬────┴──────┬───────┘  │
└───────┼─────────┼───────────┼───────────┘
        │         │           │
        └─────────┴───────────┘
                  │
                  ▼
        ┌─────────────────┐
        │    EXTRACT      │
        │  - Read data    │
        │  - Parse format │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │   TRANSFORM     │
        │  - Validate     │
        │  - Clean        │
        │  - Enrich       │
        │  - Resample     │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │      LOAD       │
        │  - Write file   │
        │  - Compress     │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  Output Files   │
        │  Parquet/CSV    │
        └─────────────────┘
```

### Installation

```bash
# Clone repository
git clone https://github.com/galafis/financial-data-etl.git
cd financial-data-etl

# Install dependencies
pip install pandas numpy

# Run pipeline
python etl_pipeline.py
```

### Quick Start

```python
from etl_pipeline import FinancialDataETL

# Initialize ETL pipeline
etl = FinancialDataETL(output_format='parquet')

# Run complete pipeline
df = etl.run_pipeline(
    source_type='api',
    source_path='BTCUSD',
    output_path='data/btcusd.parquet',
    add_indicators=True,
    resample_freq='W'
)

print(f"Processed {len(df)} rows")
```

### Extract Methods

#### CSV Extraction
```python
df = etl.extract_csv('data/market_data.csv')
```

#### JSON Extraction
```python
df = etl.extract_json('data/market_data.json')
```

#### API Extraction (Simulated)
```python
df = etl.extract_api(symbol='BTCUSD', days=365)
```

### Transform Operations

#### Data Validation
```python
# Validate OHLC relationships, remove duplicates, check for negatives
df_clean = etl.validate_data(df)

# Get quality report
report = etl.get_quality_report()
print(f"Removed {report[0]['removed_rows']} invalid rows")
```

#### Add Technical Indicators
```python
df_enriched = etl.transform_add_indicators(df)

# Available indicators:
# - SMA (20, 50 periods)
# - Returns (simple and log)
# - Volatility (20-day rolling)
# - RSI (14 periods)
# - Momentum (5, 10, 20 periods)
# - High-Low ratio
# - Volume features
```

#### Resample to Different Timeframe
```python
# Resample daily data to weekly
df_weekly = etl.transform_resample(df, freq='W')

# Resample to monthly
df_monthly = etl.transform_resample(df, freq='M')

# Available frequencies: 'D' (daily), 'W' (weekly), 'M' (monthly), 'H' (hourly)
```

### Load Methods

```python
# Load to Parquet (recommended for large datasets)
etl.load_to_file(df, 'output.parquet')

# Load to CSV
etl = FinancialDataETL(output_format='csv')
etl.load_to_file(df, 'output.csv')

# Load to JSON
etl = FinancialDataETL(output_format='json')
etl.load_to_file(df, 'output.json')
```

### Complete Pipeline Example

```python
from etl_pipeline import FinancialDataETL

# Initialize
etl = FinancialDataETL(output_format='parquet')

# Run pipeline
df = etl.run_pipeline(
    source_type='csv',
    source_path='raw_data/btcusd_daily.csv',
    output_path='processed_data/btcusd_weekly_indicators.parquet',
    add_indicators=True,
    resample_freq='W'
)

# Check results
print(f"Processed {len(df)} rows")
print(f"Columns: {df.columns.tolist()}")

# Get quality report
report = etl.get_quality_report()
for check in report:
    print(f"Initial: {check['initial_rows']}, Final: {check['final_rows']}")
    if check['issues']:
        print(f"Issues found: {check['issues']}")
```

### Data Validation Rules

1. **OHLC Integrity**:
   - High >= Low
   - High >= Open
   - High >= Close
   - Low <= Open
   - Low <= Close

2. **Price Validation**:
   - All prices must be positive
   - No NaN values in price columns

3. **Volume Validation**:
   - Volume must be non-negative
   - No NaN values in volume

4. **Duplicate Detection**:
   - Remove duplicate timestamps
   - Keep first occurrence

### Technical Indicators

| Indicator | Description | Parameters |
|-----------|-------------|------------|
| SMA | Simple Moving Average | 20, 50 periods |
| Returns | Percentage returns | 1 period |
| Log Returns | Logarithmic returns | 1 period |
| Volatility | Rolling standard deviation (annualized) | 20 periods |
| RSI | Relative Strength Index | 14 periods |
| Momentum | Price momentum | 5, 10, 20 periods |
| HL Ratio | High-Low range / Close | Intraday |

### Output Formats

#### Parquet (Recommended)
- **Pros**: Fast, compressed, columnar storage
- **Use case**: Large datasets, data warehouses
- **Size**: ~10x smaller than CSV

#### CSV
- **Pros**: Human-readable, universal compatibility
- **Use case**: Small datasets, manual inspection
- **Size**: Largest file size

#### JSON
- **Pros**: Structured, nested data support
- **Use case**: API responses, web applications
- **Size**: Medium file size

### Performance

- **Processing Speed**: 100k+ rows/second
- **Memory Efficient**: Chunked processing for large files
- **Compression**: Automatic compression for Parquet
- **Scalability**: Handles datasets up to 10M+ rows

### Use Cases

1. **Data Warehouse ETL**: Load market data into data warehouse
2. **Backtesting Preparation**: Clean and enrich data for backtesting
3. **Real-time Processing**: Stream processing with batch updates
4. **Data Quality Monitoring**: Track data quality over time
5. **Multi-timeframe Analysis**: Convert data to different timeframes

### Error Handling

```python
try:
    df = etl.run_pipeline(
        source_type='csv',
        source_path='data.csv',
        output_path='output.parquet'
    )
except FileNotFoundError:
    print("Source file not found")
except ValueError as e:
    print(f"Data validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Run pipeline with logging
etl = FinancialDataETL(output_format='parquet')
df = etl.run_pipeline(...)

# Logs will show:
# - Extraction progress
# - Validation results
# - Transformation steps
# - Load completion
```

### Integration Examples

#### With PostgreSQL
```python
import psycopg2
from sqlalchemy import create_engine

# Run ETL
df = etl.run_pipeline(...)

# Load to PostgreSQL
engine = create_engine('postgresql://user:pass@localhost/db')
df.to_sql('market_data', engine, if_exists='append', index=False)
```

#### With S3
```python
import boto3

# Run ETL
df = etl.run_pipeline(...)

# Save to S3
df.to_parquet('s3://my-bucket/data/market_data.parquet')
```

#### With Airflow
```python
from airflow import DAG
from airflow.operators.python import PythonOperator

def run_etl():
    etl = FinancialDataETL(output_format='parquet')
    etl.run_pipeline(
        source_type='api',
        source_path='BTCUSD',
        output_path='/data/btcusd.parquet'
    )

dag = DAG('financial_etl', schedule_interval='@daily')
task = PythonOperator(task_id='run_etl', python_callable=run_etl, dag=dag)
```

### Testing

```bash
# Run pipeline with sample data
python etl_pipeline.py

# Check output
ls -lh output_data.csv

# Verify data quality
python -c "import pandas as pd; df = pd.read_csv('output_data.csv'); print(df.info())"
```

### License

MIT License

### Author

**Gabriel Demetrios Lafis**

---

## Português

### Visão Geral

Pipeline ETL (Extract, Transform, Load) pronto para produção para dados de mercado financeiro com validação abrangente de qualidade de dados, cálculo de indicadores técnicos e suporte multi-formato. Projetado para plataformas de trading quantitativo e data warehouses financeiros.

### Características Principais

- **Múltiplas Fontes de Dados**: Extração de CSV, JSON, REST API
- **Validação de Dados**: Verificações de integridade OHLC, remoção de duplicatas, tratamento de valores ausentes
- **Indicadores Técnicos**: SMA, RSI, volatilidade, retornos, momentum
- **Reamostragem Temporal**: Conversão entre timeframes (tick → minuto → hora → diário → semanal)
- **Relatórios de Qualidade**: Rastreamento detalhado de qualidade de dados e registro de problemas
- **Múltiplos Formatos de Saída**: Parquet, CSV, JSON com compressão

### Casos de Uso

1. **ETL de Data Warehouse**: Carregar dados de mercado em data warehouse
2. **Preparação de Backtesting**: Limpar e enriquecer dados para backtesting
3. **Processamento em Tempo Real**: Processamento de stream com atualizações em lote
4. **Monitoramento de Qualidade de Dados**: Rastrear qualidade de dados ao longo do tempo
5. **Análise Multi-timeframe**: Converter dados para diferentes timeframes

### Autor

**Gabriel Demetrios Lafis**
