"""
Unit tests for financial-data-etl
"""

import pytest
import numpy as np
import pandas as pd
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl_pipeline import FinancialDataETL


@pytest.fixture
def etl():
    """Create an ETL instance with CSV output."""
    return FinancialDataETL(output_format='csv')


@pytest.fixture
def sample_ohlcv():
    """Generate sample OHLCV DataFrame."""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    prices = 100 * np.exp(np.cumsum(np.random.normal(0, 0.02, 100)))
    return pd.DataFrame({
        'timestamp': dates,
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, 100)),
        'high': prices * (1 + np.abs(np.random.uniform(0, 0.02, 100))),
        'low': prices * (1 - np.abs(np.random.uniform(0, 0.02, 100))),
        'close': prices,
        'volume': np.random.uniform(1e6, 5e6, 100),
    })


class TestExtract:
    def test_extract_api_returns_dataframe(self, etl):
        df = etl.extract_api('TEST', days=50)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 50

    def test_extract_api_has_ohlcv_columns(self, etl):
        df = etl.extract_api('TEST', days=30)
        for col in ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']:
            assert col in df.columns

    def test_extract_csv_from_file(self, etl, sample_ohlcv):
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            sample_ohlcv.to_csv(f.name, index=False)
            path = f.name
        try:
            df = etl.extract_csv(path)
            assert len(df) == 100
            assert 'close' in df.columns
        finally:
            os.unlink(path)

    def test_extract_csv_missing_file(self, etl):
        df = etl.extract_csv('/nonexistent/path.csv')
        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_extract_json_from_file(self, etl, sample_ohlcv):
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            sample_ohlcv.to_json(f.name, orient='records', date_format='iso')
            path = f.name
        try:
            df = etl.extract_json(path)
            assert len(df) == 100
        finally:
            os.unlink(path)


class TestValidate:
    def test_removes_duplicates(self, etl, sample_ohlcv):
        df = pd.concat([sample_ohlcv, sample_ohlcv.iloc[:5]])
        result = etl.validate_data(df)
        assert len(result) == 100

    def test_removes_negative_prices(self, etl, sample_ohlcv):
        sample_ohlcv.loc[0, 'close'] = -10
        result = etl.validate_data(sample_ohlcv)
        assert (result['close'] > 0).all()

    def test_removes_invalid_ohlc(self, etl, sample_ohlcv):
        sample_ohlcv.loc[0, 'high'] = 0.01  # high < low
        sample_ohlcv.loc[0, 'low'] = 999
        result = etl.validate_data(sample_ohlcv)
        assert len(result) < len(sample_ohlcv)

    def test_quality_report_populated(self, etl, sample_ohlcv):
        etl.validate_data(sample_ohlcv)
        report = etl.get_quality_report()
        assert len(report) == 1
        assert 'initial_rows' in report[0]
        assert 'final_rows' in report[0]


class TestTransform:
    def test_add_indicators_creates_columns(self, etl, sample_ohlcv):
        result = etl.transform_add_indicators(sample_ohlcv.copy())
        for col in ['sma_20', 'sma_50', 'returns', 'log_returns', 'volatility_20', 'rsi']:
            assert col in result.columns

    def test_rsi_in_valid_range(self, etl, sample_ohlcv):
        result = etl.transform_add_indicators(sample_ohlcv.copy())
        valid_rsi = result['rsi'].dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()

    def test_rsi_no_loss_is_100(self, etl):
        """When all price changes are positive, RSI should be 100."""
        dates = pd.date_range('2023-01-01', periods=30, freq='D')
        prices = np.arange(100, 130, dtype=float)
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices, 'high': prices + 1,
            'low': prices - 0.5, 'close': prices,
            'volume': np.ones(30) * 1e6,
        })
        result = etl.transform_add_indicators(df)
        valid_rsi = result['rsi'].dropna()
        assert (valid_rsi == 100).all()

    def test_resample_reduces_rows(self, etl, sample_ohlcv):
        result = etl.transform_resample(sample_ohlcv.copy(), 'W')
        assert len(result) < len(sample_ohlcv)

    def test_resample_preserves_ohlcv(self, etl, sample_ohlcv):
        result = etl.transform_resample(sample_ohlcv.copy(), 'W')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            assert col in result.columns


class TestPipeline:
    def test_pipeline_order_preserves_indicators(self, etl):
        """Indicators should survive when resample is also requested."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name
        try:
            df = etl.run_pipeline(
                source_type='api',
                source_path='TEST',
                output_path=output_path,
                add_indicators=True,
                resample_freq='W',
            )
            assert 'sma_20' in df.columns
            assert 'rsi' in df.columns
        finally:
            os.unlink(output_path)

    def test_pipeline_csv_output(self, etl):
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            output_path = f.name
        try:
            df = etl.run_pipeline(
                source_type='api',
                source_path='TEST',
                output_path=output_path,
                add_indicators=False,
            )
            assert os.path.exists(output_path)
            loaded = pd.read_csv(output_path)
            assert len(loaded) == len(df)
        finally:
            os.unlink(output_path)

    def test_pipeline_invalid_source(self, etl):
        with pytest.raises(ValueError):
            etl.run_pipeline(
                source_type='invalid',
                source_path='X',
                output_path='/tmp/test.csv',
            )


class TestLoadToFile:
    def test_csv_output(self, etl, sample_ohlcv):
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            path = f.name
        try:
            etl.load_to_file(sample_ohlcv, path)
            loaded = pd.read_csv(path)
            assert len(loaded) == 100
        finally:
            os.unlink(path)

    def test_json_output(self, sample_ohlcv):
        etl = FinancialDataETL(output_format='json')
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
        try:
            etl.load_to_file(sample_ohlcv, path)
            loaded = pd.read_json(path)
            assert len(loaded) == 100
        finally:
            os.unlink(path)

    def test_invalid_format(self, sample_ohlcv):
        etl = FinancialDataETL(output_format='xlsx')
        with pytest.raises(ValueError):
            etl.load_to_file(sample_ohlcv, '/tmp/test.xlsx')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
