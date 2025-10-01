"""
QVD File Processor

This module processes QVD files exported from Qlik Sense by converting them
to CSV format and then processing them with pandas for the Python BI stack.

Author: vitaBI Team
Date: 2024
"""

import os
import pandas as pd
import duckdb
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QVDProcessor:
    """
    Processes QVD files exported from Qlik Sense.
    
    This class handles the conversion of QVD files (exported as CSV) to
    optimized formats for the Python BI stack.
    """
    
    def __init__(self, data_dir: str = "./data", output_dir: str = "./data/processed"):
        """
        Initialize the QVD processor.
        
        Args:
            data_dir (str): Directory containing QVD/CSV files
            output_dir (str): Directory for processed files
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.duckdb_path = self.output_dir / "analytical_data.db"
        
        # Create directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "parquet").mkdir(exist_ok=True)
        (self.output_dir / "metadata").mkdir(exist_ok=True)
        
        # Initialize DuckDB connection
        self.conn = duckdb.connect(str(self.duckdb_path))
        
        logger.info(f"QVD Processor initialized")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def find_csv_files(self, pattern: str = "*.csv") -> List[Path]:
        """
        Find CSV files in the data directory.
        
        Args:
            pattern (str): File pattern to search for
            
        Returns:
            List[Path]: List of CSV file paths
        """
        csv_files = list(self.data_dir.glob(pattern))
        logger.info(f"Found {len(csv_files)} CSV files")
        return csv_files
    
    def process_csv_file(self, csv_path: Path) -> Dict[str, Any]:
        """
        Process a single CSV file.
        
        Args:
            csv_path (Path): Path to the CSV file
            
        Returns:
            Dict: Processing results and metadata
        """
        logger.info(f"Processing {csv_path.name}")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_path)
            
            # Get basic information
            info = {
                'file_name': csv_path.name,
                'file_path': str(csv_path),
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'data_types': {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
                'memory_usage': int(df.memory_usage(deep=True).sum()),
                'processed_at': datetime.now().isoformat()
            }
            
            # Optimize data types
            df_optimized = self._optimize_data_types(df)
            
            # Save as Parquet
            parquet_path = self.output_dir / "parquet" / f"{csv_path.stem}.parquet"
            df_optimized.to_parquet(parquet_path, index=False)
            
            # Update info with optimized data
            info['optimized_memory_usage'] = int(df_optimized.memory_usage(deep=True).sum())
            info['memory_savings'] = info['memory_usage'] - info['optimized_memory_usage']
            info['parquet_path'] = str(parquet_path)
            info['parquet_size_mb'] = round(parquet_path.stat().st_size / (1024 * 1024), 2)
            
            # Load into DuckDB
            table_name = csv_path.stem.lower().replace(' ', '_').replace('-', '_')
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM '{parquet_path}'")
            
            info['duckdb_table'] = table_name
            info['status'] = 'success'
            
            logger.info(f"✓ Processed {csv_path.name}: {info['rows']} rows, {info['columns']} columns")
            
            return info
            
        except Exception as e:
            logger.error(f"✗ Failed to process {csv_path.name}: {e}")
            return {
                'file_name': csv_path.name,
                'file_path': str(csv_path),
                'status': 'error',
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
    
    def _optimize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize data types for memory efficiency.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            
        Returns:
            pd.DataFrame: Optimized DataFrame
        """
        df_optimized = df.copy()
        
        for col in df_optimized.columns:
            col_type = df_optimized[col].dtype
            
            if col_type == 'object':
                # Try to convert to category if it has few unique values
                if df_optimized[col].nunique() / len(df_optimized) < 0.5:
                    df_optimized[col] = df_optimized[col].astype('category')
            
            elif col_type == 'int64':
                # Downcast integers
                if df_optimized[col].min() >= 0:
                    if df_optimized[col].max() < 255:
                        df_optimized[col] = df_optimized[col].astype('uint8')
                    elif df_optimized[col].max() < 65535:
                        df_optimized[col] = df_optimized[col].astype('uint16')
                    elif df_optimized[col].max() < 4294967295:
                        df_optimized[col] = df_optimized[col].astype('uint32')
                else:
                    if df_optimized[col].min() > -128 and df_optimized[col].max() < 127:
                        df_optimized[col] = df_optimized[col].astype('int8')
                    elif df_optimized[col].min() > -32768 and df_optimized[col].max() < 32767:
                        df_optimized[col] = df_optimized[col].astype('int16')
                    elif df_optimized[col].min() > -2147483648 and df_optimized[col].max() < 2147483647:
                        df_optimized[col] = df_optimized[col].astype('int32')
            
            elif col_type == 'float64':
                # Downcast floats
                df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
        
        return df_optimized
    
    def process_all_files(self) -> Dict[str, Any]:
        """
        Process all CSV files in the data directory.
        
        Returns:
            Dict: Processing summary
        """
        logger.info("Starting batch processing of CSV files")
        
        csv_files = self.find_csv_files()
        if not csv_files:
            logger.warning("No CSV files found in data directory")
            return {'status': 'no_files', 'files_processed': 0}
        
        results = []
        successful = 0
        failed = 0
        
        for csv_file in csv_files:
            result = self.process_csv_file(csv_file)
            results.append(result)
            
            if result['status'] == 'success':
                successful += 1
            else:
                failed += 1
        
        # Save processing metadata
        metadata = {
            'processing_summary': {
                'total_files': len(csv_files),
                'successful': successful,
                'failed': failed,
                'processed_at': datetime.now().isoformat()
            },
            'files': results
        }
        
        metadata_path = self.output_dir / "metadata" / "processing_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create DuckDB schema documentation
        self._create_schema_documentation()
        
        logger.info(f"Batch processing completed: {successful} successful, {failed} failed")
        
        return metadata
    
    def _create_schema_documentation(self):
        """Create schema documentation for the DuckDB database."""
        try:
            # Get all tables
            tables = self.conn.execute("SHOW TABLES").fetchall()
            
            schema_info = {
                'database_path': str(self.duckdb_path),
                'tables': {},
                'created_at': datetime.now().isoformat()
            }
            
            for table in tables:
                table_name = table[0]
                
                # Get table schema
                schema = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
                
                # Get row count
                count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                
                schema_info['tables'][table_name] = {
                    'columns': [{'name': col[0], 'type': col[1]} for col in schema],
                    'row_count': count
                }
            
            # Save schema documentation
            schema_path = self.output_dir / "metadata" / "database_schema.json"
            with open(schema_path, 'w') as f:
                json.dump(schema_info, f, indent=2)
            
            logger.info("Schema documentation created")
            
        except Exception as e:
            logger.error(f"Failed to create schema documentation: {e}")
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a specific table.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            Dict: Table information
        """
        try:
            # Get basic info
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            schema = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
            
            # Get sample data
            sample = self.conn.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchall()
            
            return {
                'table_name': table_name,
                'row_count': count,
                'columns': [{'name': col[0], 'type': col[1]} for col in schema],
                'sample_data': sample
            }
            
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            return {'error': str(e)}
    
    def query_data(self, query: str) -> pd.DataFrame:
        """
        Execute a query on the DuckDB database.
        
        Args:
            query (str): SQL query
            
        Returns:
            pd.DataFrame: Query results
        """
        try:
            result = self.conn.execute(query).fetchdf()
            return result
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close the DuckDB connection."""
        if self.conn:
            self.conn.close()
            logger.info("DuckDB connection closed")


# Example usage
if __name__ == "__main__":
    # Initialize processor
    processor = QVDProcessor(
        data_dir="./data/csv_exports",
        output_dir="./data/processed"
    )
    
    try:
        # Process all files
        results = processor.process_all_files()
        
        print("Processing Results:")
        print(f"Total files: {results['processing_summary']['total_files']}")
        print(f"Successful: {results['processing_summary']['successful']}")
        print(f"Failed: {results['processing_summary']['failed']}")
        
        # Get table information
        tables = processor.conn.execute("SHOW TABLES").fetchall()
        print(f"\nTables created: {[table[0] for table in tables]}")
        
        # Example query
        if tables:
            table_name = tables[0][0]
            info = processor.get_table_info(table_name)
            print(f"\nTable '{table_name}' info:")
            print(f"Rows: {info['row_count']}")
            print(f"Columns: {len(info['columns'])}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        processor.close()

