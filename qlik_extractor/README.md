# Qlik Sense Data Extraction Tools

This module provides a simple and practical approach for extracting data from Qlik Sense and processing it for a Python-based BI stack.

## Features

- **Simple Export Process**: Manual QVD/CSV export from Qlik Sense (no API complexity)
- **Automated Processing**: Convert exported CSV files to optimized formats
- **Data Optimization**: Memory-efficient data type optimization
- **DuckDB Integration**: Store processed data in DuckDB for analytical queries
- **Parquet Storage**: Efficient columnar storage format
- **Complete Workflow**: Step-by-step guided process

## Installation

1. Install dependencies:
```bash
pip install -r qlik_extractor/requirements.txt
```

2. Set up data directories:
```bash
mkdir -p data/csv_exports
mkdir -p data/processed
```

## Quick Start

### Option 1: Guided Workflow (Recommended)

Run the complete guided workflow:

```bash
python qlik_extractor/data_extraction_workflow.py
```

This will walk you through:
1. Exporting data from Qlik Sense
2. Processing the exported files
3. Verifying the results
4. Next steps

### Option 2: Manual Process

1. **Export from Qlik Sense**:
   - Open your Qlik Sense application
   - Go to Data Load Editor
   - Use the script in `qlik_export_script.txt`
   - Save CSV files to `data/csv_exports/`

2. **Process the Data**:
```python
from qlik_extractor.qvd_processor import QVDProcessor

# Initialize processor
processor = QVDProcessor(
    data_dir="./data/csv_exports",
    output_dir="./data/processed"
)

# Process all CSV files
results = processor.process_all_files()

# Query the data
sales_data = processor.query_data("SELECT * FROM salesdata LIMIT 10")
print(sales_data)
```

## Usage

### Basic Usage

```python
from qlik_extractor.qrs_client import QRSAPIClient
from qlik_extractor.config import get_qrs_config

# Get configuration from environment
config = get_qrs_config()

# Initialize client
client = QRSAPIClient(
    base_url=config.base_url,
    username=config.username,
    password=config.password,
    user_directory=config.user_directory
)

# Test connection
if client.test_connection():
    print("Connected successfully!")
    
    # Get apps
    apps = client.get_apps(limit=10)
    print(f"Found {len(apps)} apps")
    
    # Get data connections
    connections = client.get_data_connections(limit=10)
    print(f"Found {len(connections)} data connections")

# Close client
client.close()
```

### Advanced Usage

```python
from qlik_extractor.qrs_client import QRSAPIClient

# Initialize with custom settings
client = QRSAPIClient(
    base_url="https://qlikserver.domain.com:4242",
    username="admin",
    password="password",
    user_directory="DOMAIN",
    verify_ssl=True
)

try:
    # Test connection
    if not client.test_connection():
        raise Exception("Failed to connect to QRS API")
    
    # Get specific app
    app = client.get_app("app-id-here")
    if app:
        print(f"App: {app['name']}")
        
        # Get data model
        data_model = client.get_app_data_model("app-id-here")
        if data_model:
            print("Data model retrieved successfully")
        
        # Get load script
        script = client.get_app_script("app-id-here")
        if script:
            print("Load script retrieved successfully")
    
    # Get all apps with pagination
    all_apps = []
    offset = 0
    limit = 100
    
    while True:
        apps = client.get_apps(limit=limit, offset=offset)
        if not apps:
            break
        all_apps.extend(apps)
        offset += limit
        if len(apps) < limit:
            break
    
    print(f"Total apps: {len(all_apps)}")

finally:
    client.close()
```

## Testing

Run the test suite to validate the QRS API client:

```bash
python qlik_extractor/test_qrs_client.py
```

The test suite will:
1. Test connection to QRS API
2. Retrieve and validate apps
3. Retrieve and validate data connections
4. Retrieve and validate users
5. Provide a comprehensive test summary

## API Reference

### QRSAPIClient

#### Constructor
```python
QRSAPIClient(base_url, username, password, user_directory="DOMAIN", verify_ssl=True)
```

#### Methods

- `test_connection()` - Test connection to QRS API
- `get_apps(limit=100, offset=0)` - Retrieve list of applications
- `get_app(app_id)` - Retrieve specific application
- `get_data_connections(limit=100, offset=0)` - Retrieve list of data connections
- `get_data_connection(connection_id)` - Retrieve specific data connection
- `get_app_data_model(app_id)` - Retrieve data model for application
- `get_app_script(app_id)` - Retrieve load script for application
- `get_users(limit=100, offset=0)` - Retrieve list of users
- `close()` - Close the session and clean up resources

## Error Handling

The client includes comprehensive error handling:

- **Rate Limiting**: Automatic handling of HTTP 429 responses with exponential backoff
- **Retry Logic**: Configurable retry attempts for failed requests
- **SSL Verification**: Optional SSL certificate verification
- **Timeout Handling**: Configurable request timeouts
- **Logging**: Detailed logging for debugging and monitoring

## Security Considerations

1. **Use HTTPS**: Always use HTTPS for API communications
2. **Certificate Management**: Properly manage client certificates for production
3. **Environment Variables**: Store sensitive information in environment variables
4. **CSRF Protection**: The client automatically includes X-Qlik-xrfkey headers
5. **User Context**: Proper user context is included in all requests

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check the base URL and port (default: 4242)
2. **Authentication Failed**: Verify username, password, and user directory
3. **SSL Errors**: Check certificate configuration and SSL verification settings
4. **Rate Limiting**: Implement proper retry logic for high-volume requests

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support, please open an issue in the GitHub repository.
