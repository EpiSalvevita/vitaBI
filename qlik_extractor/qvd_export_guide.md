# QVD File Export Guide

## Overview
This guide explains how to manually export QVD files from Qlik Sense and process them in Python. This approach is simpler and more practical than API integration for most use cases.

## Manual QVD Export Process

### Method 1: Using Qlik Sense Data Load Editor

1. **Open Qlik Sense Application**
   - Launch Qlik Sense Desktop or access Qlik Sense Hub
   - Open the application containing the data you want to export

2. **Access Data Load Editor**
   - Navigate to the "Data Load Editor" tab
   - View the current load script

3. **Add Export Statements**
   Add `STORE` statements to export tables as QVD files:
   ```sql
   // Export all tables as QVD files
   FOR vCount = 0 to NoOfTables()-1
       LET vTableName = TableName($(vCount));
       STORE '$(vTableName)' INTO 'lib://DataFiles/$(vTableName).qvd' (qvd);
   NEXT vCount
   
   // Or export specific tables
   STORE SalesData INTO 'lib://DataFiles/SalesData.qvd' (qvd);
   STORE CustomerData INTO 'lib://DataFiles/CustomerData.qvd' (qvd);
   STORE ProductData INTO 'lib://DataFiles/ProductData.qvd' (qvd);
   ```

4. **Reload the Application**
   - Click "Load Data" to execute the script
   - QVD files will be created in the specified folder

### Method 2: Export from Visualizations

1. **Select Visualization**
   - Navigate to the sheet with the data you want to export
   - Click on the visualization

2. **Export Data**
   - Click the "More" options (three dots)
   - Select "Export data"
   - Choose format (Excel, CSV, etc.)

3. **Convert to QVD**
   - Import the exported data back into Qlik Sense
   - Use `STORE` statement to save as QVD

## QVD File Structure

QVD files are Qlik's native data format with the following characteristics:
- **Binary format**: Optimized for fast loading
- **Compressed**: Efficient storage
- **Metadata included**: Table structure and field information
- **Cross-platform**: Can be read by Qlik Sense and QlikView

## Python Processing Options

Since direct QVD reading libraries are limited, we'll use these approaches:

### Option 1: Convert QVD to CSV in Qlik Sense
```sql
// In Qlik Sense Data Load Editor
LOAD * FROM 'lib://DataFiles/YourTable.qvd' (qvd);
STORE YourTable INTO 'lib://DataFiles/YourTable.csv' (txt);
```

### Option 2: Use Qlik Sense Engine API (Advanced)
- Connect to Qlik Sense Engine
- Load QVD files through the engine
- Export data via Engine API

### Option 3: Manual CSV Export + Python Processing
- Export data as CSV from Qlik Sense
- Process CSV files with pandas
- Convert to Parquet for better performance

## Recommended Workflow

1. **Export QVD Files**
   - Use Qlik Sense to export all necessary tables as QVD files
   - Store in a dedicated folder (e.g., `./data/qlik_exports/`)

2. **Convert to CSV**
   - Create a simple Qlik Sense script to convert QVD to CSV
   - This ensures data compatibility with Python

3. **Python Processing**
   - Use pandas to read CSV files
   - Convert to Parquet format for better performance
   - Store in DuckDB for analytical queries

## File Organization

```
data/
├── qlik_exports/          # Original QVD files
│   ├── SalesData.qvd
│   ├── CustomerData.qvd
│   └── ProductData.qvd
├── csv_exports/           # Converted CSV files
│   ├── SalesData.csv
│   ├── CustomerData.csv
│   └── ProductData.csv
├── parquet/              # Optimized Parquet files
│   ├── SalesData.parquet
│   ├── CustomerData.parquet
│   └── ProductData.parquet
└── analytical_data.db    # DuckDB database
```

## Benefits of This Approach

1. **Simplicity**: No complex API integration required
2. **Reliability**: Uses Qlik Sense's native export functionality
3. **Flexibility**: Can export any data from Qlik Sense
4. **Performance**: QVD files are optimized for fast loading
5. **Compatibility**: Works with any Qlik Sense version

## Next Steps

1. Export QVD files from your Qlik Sense applications
2. Set up the Python processing pipeline
3. Convert QVD files to CSV format
4. Process CSV files with pandas
5. Store in DuckDB for analytical queries

## Troubleshooting

### Common Issues
- **File Path Errors**: Ensure the data connection path exists
- **Permission Issues**: Check file system permissions
- **Memory Issues**: For large datasets, consider batch processing
- **Encoding Issues**: Ensure proper character encoding for CSV files

### Best Practices
- Test with small datasets first
- Use descriptive file names
- Document the export process
- Keep original QVD files as backup
- Monitor file sizes and processing times

