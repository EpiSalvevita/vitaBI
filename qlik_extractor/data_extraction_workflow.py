"""
Data Extraction Workflow

This script provides a complete workflow for extracting data from Qlik Sense
and processing it for the Python BI stack.

Author: vitaBI Team
Date: 2024
"""

import os
import sys
from pathlib import Path
import logging

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qlik_extractor.qvd_processor import QVDProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataExtractionWorkflow:
    """
    Complete workflow for data extraction from Qlik Sense.
    
    This class orchestrates the entire process from QVD export to
    optimized data storage in DuckDB.
    """
    
    def __init__(self, project_root: str = "."):
        """
        Initialize the data extraction workflow.
        
        Args:
            project_root (str): Root directory of the project
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.csv_exports_dir = self.data_dir / "csv_exports"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories
        self._setup_directories()
        
        # Initialize processor
        self.processor = QVDProcessor(
            data_dir=str(self.csv_exports_dir),
            output_dir=str(self.processed_dir)
        )
        
        logger.info("Data Extraction Workflow initialized")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"CSV exports: {self.csv_exports_dir}")
        logger.info(f"Processed data: {self.processed_dir}")
    
    def _setup_directories(self):
        """Create necessary directories."""
        directories = [
            self.data_dir,
            self.csv_exports_dir,
            self.processed_dir,
            self.processed_dir / "parquet",
            self.processed_dir / "metadata"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def step1_export_instructions(self):
        """Display instructions for Qlik Sense export."""
        print("\n" + "="*60)
        print("STEP 1: EXPORT DATA FROM QLIK SENSE")
        print("="*60)
        print("\n1. Open your Qlik Sense application")
        print("2. Go to the Data Load Editor")
        print("3. Copy and paste this script:")
        print("\n" + "-"*40)
        print("// Export all tables as CSV files")
        print("FOR vCount = 0 to NoOfTables()-1")
        print("    LET vTableName = TableName($(vCount));")
        print("    LET vCsvFile = 'lib://DataFiles/' & '$(vTableName)' & '.csv';")
        print("    STORE [$(vTableName)] INTO [$(vCsvFile)] (txt);")
        print("NEXT vCount")
        print("-"*40)
        print("\n4. Modify 'lib://DataFiles/' to point to your data folder")
        print("5. Click 'Load Data' to execute the script")
        print("6. Copy the exported CSV files to:", self.csv_exports_dir)
        print("\nPress Enter when you have completed the export...")
        input()
    
    def step2_process_data(self):
        """Process the exported CSV files."""
        print("\n" + "="*60)
        print("STEP 2: PROCESS EXPORTED DATA")
        print("="*60)
        
        # Check if CSV files exist
        csv_files = list(self.csv_exports_dir.glob("*.csv"))
        if not csv_files:
            print(f"❌ No CSV files found in {self.csv_exports_dir}")
            print("Please export your data from Qlik Sense first.")
            return False
        
        print(f"✅ Found {len(csv_files)} CSV files to process")
        
        # Process files
        try:
            results = self.processor.process_all_files()
            
            print("\nProcessing Results:")
            print(f"  Total files: {results['processing_summary']['total_files']}")
            print(f"  Successful: {results['processing_summary']['successful']}")
            print(f"  Failed: {results['processing_summary']['failed']}")
            
            # Show file details
            print("\nFile Details:")
            for file_info in results['files']:
                if file_info['status'] == 'success':
                    print(f"  ✅ {file_info['file_name']}: {file_info['rows']} rows, {file_info['columns']} columns")
                    print(f"     Memory savings: {file_info['memory_savings']:,} bytes")
                    print(f"     Parquet size: {file_info['parquet_size_mb']:.2f} MB")
                else:
                    print(f"  ❌ {file_info['file_name']}: {file_info['error']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Processing failed: {e}")
            return False
    
    def step3_verify_data(self):
        """Verify the processed data."""
        print("\n" + "="*60)
        print("STEP 3: VERIFY PROCESSED DATA")
        print("="*60)
        
        try:
            # Get database tables
            tables = self.processor.conn.execute("SHOW TABLES").fetchall()
            
            if not tables:
                print("❌ No tables found in database")
                return False
            
            print(f"✅ Found {len(tables)} tables in DuckDB database")
            
            # Show table information
            print("\nTable Information:")
            for table in tables:
                table_name = table[0]
                info = self.processor.get_table_info(table_name)
                print(f"  📊 {table_name}: {info['row_count']} rows, {len(info['columns'])} columns")
            
            # Test queries
            print("\nTesting Queries:")
            self._test_basic_queries()
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def _test_basic_queries(self):
        """Test basic queries on the processed data."""
        try:
            # Get first table for testing
            tables = self.processor.conn.execute("SHOW TABLES").fetchall()
            if not tables:
                return
            
            table_name = tables[0][0]
            
            # Test 1: Basic select
            print(f"\n  🔍 Testing basic select from {table_name}:")
            result = self.processor.query_data(f"SELECT * FROM {table_name} LIMIT 3")
            if not result.empty:
                print(f"     ✅ Retrieved {len(result)} rows")
                print(f"     Columns: {list(result.columns)}")
            else:
                print("     ❌ No data returned")
            
            # Test 2: Count query
            print(f"\n  🔢 Testing count query on {table_name}:")
            count_result = self.processor.query_data(f"SELECT COUNT(*) as total_rows FROM {table_name}")
            if not count_result.empty:
                total_rows = count_result.iloc[0]['total_rows']
                print(f"     ✅ Total rows: {total_rows:,}")
            
        except Exception as e:
            print(f"     ❌ Query test failed: {e}")
    
    def step4_next_steps(self):
        """Display next steps."""
        print("\n" + "="*60)
        print("STEP 4: NEXT STEPS")
        print("="*60)
        print("\n🎉 Data extraction completed successfully!")
        print("\nNext steps:")
        print("1. 📊 Build your Python dashboard using the processed data")
        print("2. 🔗 Add API integration for relationships and KPIs (optional)")
        print("3. 🚀 Deploy your Python BI solution")
        print(f"\nYour data is now available in: {self.processed_dir}")
        print(f"Database file: {self.processor.duckdb_path}")
        print(f"Parquet files: {self.processed_dir / 'parquet'}")
    
    def run_complete_workflow(self):
        """Run the complete data extraction workflow."""
        print("🚀 Starting Qlik Sense Data Extraction Workflow")
        print("=" * 60)
        
        try:
            # Step 1: Export instructions
            self.step1_export_instructions()
            
            # Step 2: Process data
            if not self.step2_process_data():
                print("❌ Data processing failed. Please check your CSV files.")
                return False
            
            # Step 3: Verify data
            if not self.step3_verify_data():
                print("❌ Data verification failed. Please check the processing results.")
                return False
            
            # Step 4: Next steps
            self.step4_next_steps()
            
            print("\n✅ Workflow completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            return False
        
        finally:
            self.processor.close()


def main():
    """Main function to run the workflow."""
    workflow = DataExtractionWorkflow()
    success = workflow.run_complete_workflow()
    
    if success:
        print("\n🎉 All done! Your data is ready for Python BI.")
    else:
        print("\n❌ Workflow failed. Please check the errors above.")


if __name__ == "__main__":
    main()
