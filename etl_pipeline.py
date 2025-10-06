"""
Financial Data ETL Pipeline
Author: Gabriel Demetrios Lafis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialDataETL:
    """
    ETL Pipeline for financial market data.
    Extract from multiple sources, Transform with validation, Load to database.
    """
    
    def __init__(self, output_format: str = 'parquet'):
        self.output_format = output_format
        self.data_quality_report = []
        
    def extract_csv(self, filepath: str) -> pd.DataFrame:
        """Extract data from CSV file"""
        logger.info(f"Extracting data from {filepath}")
        try:
            df = pd.read_csv(filepath, parse_dates=['timestamp'])
            logger.info(f"Extracted {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error extracting CSV: {e}")
            return pd.DataFrame()
    
    def extract_json(self, filepath: str) -> pd.DataFrame:
        """Extract data from JSON file"""
        logger.info(f"Extracting data from {filepath}")
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            logger.info(f"Extracted {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
            return pd.DataFrame()
    
    def extract_api(self, symbol: str, days: int = 365) -> pd.DataFrame:
        """Simulate API extraction (placeholder)"""
        logger.info(f"Extracting {symbol} data from API for {days} days")
        
        # Generate synthetic data
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        price = 100.0
        data = []
        
        for date in dates:
            price *= (1 + np.random.normal(0.001, 0.02))
            data.append({
                'timestamp': date,
                'symbol': symbol,
                'open': price * (1 + np.random.uniform(-0.01, 0.01)),
                'high': price * (1 + np.random.uniform(0, 0.02)),
                'low': price * (1 - np.random.uniform(0, 0.02)),
                'close': price,
                'volume': np.random.uniform(1e6, 5e6)
            })
        
        df = pd.DataFrame(data)
        logger.info(f"Extracted {len(df)} rows")
        return df
    
    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate data quality"""
        logger.info("Validating data quality...")
        
        initial_rows = len(df)
        issues = []
        
        # Check for missing values
        missing = df.isnull().sum()
        if missing.any():
            issues.append(f"Missing values: {missing[missing > 0].to_dict()}")
        
        # Check for duplicates
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues.append(f"Duplicate rows: {duplicates}")
            df = df.drop_duplicates()
        
        # Validate OHLC relationships
        if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
            invalid_ohlc = (
                (df['high'] < df['low']) |
                (df['high'] < df['open']) |
                (df['high'] < df['close']) |
                (df['low'] > df['open']) |
                (df['low'] > df['close'])
            )
            if invalid_ohlc.any():
                issues.append(f"Invalid OHLC relationships: {invalid_ohlc.sum()} rows")
                df = df[~invalid_ohlc]
        
        # Check for negative prices
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in df.columns:
                negative = (df[col] <= 0).sum()
                if negative > 0:
                    issues.append(f"Negative {col}: {negative} rows")
                    df = df[df[col] > 0]
        
        # Check for negative volume
        if 'volume' in df.columns:
            negative_vol = (df['volume'] < 0).sum()
            if negative_vol > 0:
                issues.append(f"Negative volume: {negative_vol} rows")
                df = df[df['volume'] >= 0]
        
        final_rows = len(df)
        removed = initial_rows - final_rows
        
        self.data_quality_report.append({
            'timestamp': datetime.now(),
            'initial_rows': initial_rows,
            'final_rows': final_rows,
            'removed_rows': removed,
            'issues': issues
        })
        
        logger.info(f"Validation complete. Removed {removed} rows")
        return df
    
    def transform_add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators"""
        logger.info("Adding technical indicators...")
        
        if 'close' in df.columns:
            # Simple Moving Averages
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            # Returns
            df['returns'] = df['close'].pct_change()
            df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
            
            # Volatility
            df['volatility_20'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        logger.info(f"Added indicators. Shape: {df.shape}")
        return df
    
    def transform_resample(self, df: pd.DataFrame, freq: str = 'W') -> pd.DataFrame:
        """Resample data to different frequency"""
        logger.info(f"Resampling to {freq} frequency...")
        
        if 'timestamp' not in df.columns:
            logger.error("No timestamp column found")
            return df
        
        df = df.set_index('timestamp')
        
        resampled = df.resample(freq).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        logger.info(f"Resampled to {len(resampled)} rows")
        return resampled.reset_index()
    
    def load_to_file(self, df: pd.DataFrame, filepath: str):
        """Load data to file"""
        logger.info(f"Loading data to {filepath}")
        
        if self.output_format == 'parquet':
            df.to_parquet(filepath, index=False)
        elif self.output_format == 'csv':
            df.to_csv(filepath, index=False)
        elif self.output_format == 'json':
            df.to_json(filepath, orient='records', date_format='iso')
        else:
            raise ValueError(f"Unknown format: {self.output_format}")
        
        logger.info(f"Successfully loaded {len(df)} rows")
    
    def run_pipeline(self, 
                    source_type: str,
                    source_path: str,
                    output_path: str,
                    add_indicators: bool = True,
                    resample_freq: Optional[str] = None) -> pd.DataFrame:
        """
        Run complete ETL pipeline.
        
        Args:
            source_type: 'csv', 'json', or 'api'
            source_path: Path to source file or API symbol
            output_path: Path to output file
            add_indicators: Whether to add technical indicators
            resample_freq: Resampling frequency (e.g., 'W', 'M')
        """
        logger.info("=== Starting ETL Pipeline ===")
        
        # Extract
        if source_type == 'csv':
            df = self.extract_csv(source_path)
        elif source_type == 'json':
            df = self.extract_json(source_path)
        elif source_type == 'api':
            df = self.extract_api(source_path)
        else:
            raise ValueError(f"Unknown source type: {source_type}")
        
        if df.empty:
            logger.error("No data extracted")
            return df
        
        # Transform
        df = self.validate_data(df)
        
        if add_indicators:
            df = self.transform_add_indicators(df)
        
        if resample_freq:
            df = self.transform_resample(df, resample_freq)
        
        # Load
        self.load_to_file(df, output_path)
        
        logger.info("=== ETL Pipeline Complete ===")
        return df
    
    def get_quality_report(self) -> List[Dict]:
        """Get data quality report"""
        return self.data_quality_report

if __name__ == "__main__":
    # Example usage
    etl = FinancialDataETL(output_format='csv')
    
    # Run pipeline with API source
    df = etl.run_pipeline(
        source_type='api',
        source_path='BTCUSD',
        output_path='output_data.csv',
        add_indicators=True,
        resample_freq='W'
    )
    
    print(f"\nProcessed {len(df)} rows")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst few rows:\n{df.head()}")
    
    # Quality report
    report = etl.get_quality_report()
    print(f"\nQuality Report: {len(report)} checks performed")
    
    print("\n✓ ETL Pipeline executed successfully!")
