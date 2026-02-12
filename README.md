# Financial Data ETL Pipeline

Pipeline ETL para dados financeiros de mercado com validacao de qualidade e indicadores tecnicos.

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-2.0+-150458.svg)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Portugues](#portugues) | [English](#english)

---

## Portugues

### Sobre

Pipeline ETL (Extract, Transform, Load) para dados financeiros de mercado. Implementado em um unico modulo Python (`etl_pipeline.py`) com a classe `FinancialDataETL` que:

**Extracao:**
- CSV (com parse automatico de coluna `timestamp`)
- JSON
- API simulada (gera dados sinteticos OHLCV para testes)

**Validacao:**
- Remove linhas duplicadas
- Valida relacoes OHLC (high >= low, high >= open/close, low <= open/close)
- Remove precos negativos ou zerados
- Remove volumes negativos
- Gera relatorio de qualidade com contagem de linhas removidas e problemas encontrados

**Transformacao:**
- Medias moveis simples (SMA 20 e 50 dias)
- Retornos percentuais e logaritmicos
- Volatilidade anualizada (janela de 20 dias)
- RSI (14 periodos) com tratamento de divisao por zero

**Carga:**
- Exporta para CSV, JSON ou Parquet (Parquet requer `pyarrow`)

### Como Usar

```bash
# Clonar o repositorio
git clone https://github.com/galafis/financial-data-etl.git
cd financial-data-etl

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Executar exemplo com dados sinteticos
python etl_pipeline.py

# Executar testes
pytest tests/ -v
```

### Uso Programatico

```python
from etl_pipeline import FinancialDataETL

# Criar pipeline com saida CSV
etl = FinancialDataETL(output_format='csv')

# Executar pipeline completo
df = etl.run_pipeline(
    source_type='api',        # 'csv', 'json' ou 'api'
    source_path='BTCUSD',     # caminho do arquivo ou simbolo
    output_path='saida.csv',
    add_indicators=True,      # adicionar indicadores tecnicos
    resample_freq='W',        # resample semanal (opcional)
)

# Ver relatorio de qualidade
print(etl.get_quality_report())
```

### Estrutura do Projeto

```
financial-data-etl/
├── etl_pipeline.py    # Classe FinancialDataETL (extracao, validacao, transformacao, carga)
├── tests/
│   ├── __init__.py
│   └── test_main.py   # 22 testes funcionais
├── requirements.txt
├── LICENSE
└── README.md
```

### Tecnologias

- **Python 3.9+** — linguagem principal
- **pandas 2.0+** — manipulacao de dados e series temporais
- **NumPy 1.23+** — computacao numerica

### Limitacoes

- A extracao via API gera dados sinteticos — nao se conecta a APIs reais de mercado
- Nao implementa processamento paralelo ou distribuido
- Nao possui monitoramento, alertas ou configuracao via YAML
- Nao inclui Dockerfile ou CI/CD
- Erros de extracao (arquivo nao encontrado, formato invalido) sao logados e retornam DataFrame vazio silenciosamente

---

## English

### About

ETL (Extract, Transform, Load) pipeline for financial market data. Implemented in a single Python module (`etl_pipeline.py`) with the `FinancialDataETL` class that:

**Extraction:**
- CSV (with automatic `timestamp` column parsing)
- JSON
- Simulated API (generates synthetic OHLCV data for testing)

**Validation:**
- Removes duplicate rows
- Validates OHLC relationships (high >= low, high >= open/close, low <= open/close)
- Removes negative or zero prices
- Removes negative volumes
- Generates quality report with row removal counts and issues found

**Transformation:**
- Simple moving averages (SMA 20 and 50 days)
- Percent and log returns
- Annualized volatility (20-day window)
- RSI (14 periods) with division-by-zero handling

**Loading:**
- Exports to CSV, JSON, or Parquet (Parquet requires `pyarrow`)

### Usage

```bash
# Clone the repository
git clone https://github.com/galafis/financial-data-etl.git
cd financial-data-etl

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run example with synthetic data
python etl_pipeline.py

# Run tests
pytest tests/ -v
```

### Programmatic Usage

```python
from etl_pipeline import FinancialDataETL

# Create pipeline with CSV output
etl = FinancialDataETL(output_format='csv')

# Run complete pipeline
df = etl.run_pipeline(
    source_type='api',        # 'csv', 'json', or 'api'
    source_path='BTCUSD',     # file path or symbol
    output_path='output.csv',
    add_indicators=True,      # add technical indicators
    resample_freq='W',        # weekly resample (optional)
)

# View quality report
print(etl.get_quality_report())
```

### Project Structure

```
financial-data-etl/
├── etl_pipeline.py    # FinancialDataETL class (extraction, validation, transformation, loading)
├── tests/
│   ├── __init__.py
│   └── test_main.py   # 22 functional tests
├── requirements.txt
├── LICENSE
└── README.md
```

### Technologies

- **Python 3.9+** — core language
- **pandas 2.0+** — data manipulation and time series
- **NumPy 1.23+** — numerical computing

### Limitations

- API extraction generates synthetic data — does not connect to real market APIs
- Does not implement parallel or distributed processing
- Has no monitoring, alerting, or YAML configuration
- Does not include Dockerfile or CI/CD
- Extraction errors (file not found, invalid format) are logged and silently return an empty DataFrame

---

## Autor / Author

**Gabriel Demetrios Lafis**
- GitHub: [@galafis](https://github.com/galafis)
- LinkedIn: [Gabriel Demetrios Lafis](https://linkedin.com/in/gabriel-demetrios-lafis)

## Licenca / License

MIT License - veja [LICENSE](LICENSE) para detalhes / see [LICENSE](LICENSE) for details.
