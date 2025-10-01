"""
Test script for QVD processor.

This script demonstrates how to use the QVD processor to convert
CSV files (exported from Qlik Sense) to optimized formats.

Author: vitaBI Team
Date: 2024
"""

import os
import sys
import pandas as pd
import tempfile
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qlik_extractor.qvd_processor import QVDProcessor


def create_sample_data():
    """Create sample CSV files for testing."""
    print("Creating sample data...")
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    csv_dir = temp_dir / "csv_exports"
    csv_dir.mkdir()
    
    # Sample sales data
    sales_data = {
        'Date': pd.date_range('2023-01-01', periods=1000, freq='D'),
        'ProductID': [f'P{i%100:03d}' for i in range(1000)],
        'CustomerID': [f'C{i%50:03d}' for i in range(1000)],
        'Sales': [100 + i * 0.5 + (i % 10) * 10 for i in range(1000)],
        'Quantity': [1 + (i % 5) for i in range(1000)],
        'Region': [['North', 'South', 'East', 'West'][i % 4] for i in range(1000)]
    }
    sales_df = pd.DataFrame(sales_data)
    sales_df.to_csv(csv_dir / "SalesData.csv", index=False)
    
    # Sample customer data
    customer_data = {
        'CustomerID': [f'C{i:03d}' for i in range(50)],
        'CustomerName': [f'Customer {i}' for i in range(50)],
        'City': [f'City {i%10}' for i in range(50)],
        'Country': [['USA', 'Canada', 'Mexico'][i % 3] for i in range(50)],
        'Segment': [['Enterprise', 'SMB', 'Consumer'][i % 3] for i in range(50)]
    }
    customer_df = pd.DataFrame(customer_data)
    customer_df.to_csv(csv_dir / "CustomerData.csv", index=False)
    
    # Sample product data
    product_data = {
        'ProductID': [f'P{i:03d}' for i in range(100)],
        'ProductName': [f'Product {i}' for i in range(100)],
        'Category': [f'Category {i%10}' for i in range(100)],
        'Price': [10 + i * 0.1 for i in range(100)],
        'Cost': [5 + i * 0.05 for i in range(100)]
    }
    product_df = pd.DataFrame(product_data)
    product_df.to_csv(csv_dir / "ProductData.csv", index=False)
    
    print(f"Sample data created in: {csv_dir}")
    return csv_dir


def test_qvd_processor():
    """Test the QVD processor with sample data."""
    print("Testing QVD Processor...")
    
    # Create sample data
    csv_dir = create_sample_data()
    
    # Initialize processor
    processor = QVDProcessor(
        data_dir=str(csv_dir),
        output_dir="./test_output"
    )
    
    try:
        # Process all files
        print("\nProcessing CSV files...")
        results = processor.process_all_files()
        
        # Print results
        print("\n" + "="*50)
        print("PROCESSING RESULTS")
        print("="*50)
        print(f"Total files: {results['processing_summary']['total_files']}")
        print(f"Successful: {results['processing_summary']['successful']}")
        print(f"Failed: {results['processing_summary']['failed']}")
        
        # Show file details
        print("\nFile Details:")
        for file_info in results['files']:
            if file_info['status'] == 'success':
                print(f"✓ {file_info['file_name']}: {file_info['rows']} rows, {file_info['columns']} columns")
                print(f"  Memory savings: {file_info['memory_savings']:,} bytes")
                print(f"  Parquet size: {file_info['parquet_size_mb']:.2f} MB")
            else:
                print(f"✗ {file_info['file_name']}: {file_info['error']}")
        
        # Show database tables
        print("\nDatabase Tables:")
        tables = processor.conn.execute("SHOW TABLES").fetchall()
        for table in tables:
            table_name = table[0]
            info = processor.get_table_info(table_name)
            print(f"  {table_name}: {info['row_count']} rows, {len(info['columns'])} columns")
        
        # Test queries
        print("\nTesting Queries:")
        
        # Query 1: Basic aggregation
        query1 = """
        SELECT 
            Region,
            COUNT(*) as OrderCount,
            SUM(Sales) as TotalSales,
            AVG(Sales) as AvgSales
        FROM salesdata 
        GROUP BY Region 
        ORDER BY TotalSales DESC
        """
        result1 = processor.query_data(query1)
        print("\nSales by Region:")
        print(result1.to_string(index=False))
        
        # Query 2: Join with customer data
        query2 = """
        SELECT 
            c.CustomerName,
            c.City,
            COUNT(*) as OrderCount,
            SUM(s.Sales) as TotalSales
        FROM salesdata s
        JOIN customerdata c ON s.CustomerID = c.CustomerID
        GROUP BY c.CustomerName, c.City
        ORDER BY TotalSales DESC
        LIMIT 10
        """
        result2 = processor.query_data(query2)
        print("\nTop Customers by Sales:")
        print(result2.to_string(index=False))
        
        # Query 3: Product performance
        query3 = """
        SELECT 
            p.ProductName,
            p.Category,
            COUNT(*) as OrderCount,
            SUM(s.Sales) as TotalSales,
            AVG(s.Sales) as AvgSales
        FROM salesdata s
        JOIN productdata p ON s.ProductID = p.ProductID
        GROUP BY p.ProductName, p.Category
        ORDER BY TotalSales DESC
        LIMIT 10
        """
        result3 = processor.query_data(query3)
        print("\nTop Products by Sales:")
        print(result3.to_string(index=False))
        
        print("\n✓ QVD Processor test completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        processor.close()
        
        # Clean up test data
        import shutil
        shutil.rmtree(csv_dir)
        print(f"\nCleaned up test data from: {csv_dir}")


if __name__ == "__main__":
    test_qvd_processor()

