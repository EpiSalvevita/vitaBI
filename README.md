# Qlik Sense to Python BI Migration

A Python-based Business Intelligence solution designed to replace Qlik Sense, optimized for large datasets (170M+ rows) with cost-effective local deployment.

## Project Overview

This project migrates from Qlik Sense to a modern Python-based BI stack, focusing on:
- **Cost minimization** through open-source tools
- **High performance** with DuckDB for analytical queries
- **Scalability** with a clear migration path for future growth
- **User-friendly** dashboards with Streamlit and Plotly

## Architecture

```
Qlik Sense → QVD/CSV Export → Pandas → Parquet → DuckDB → FastAPI → Streamlit
                ↓
        Data Model Analysis → SQLite (Metadata) → User Management
                ↓
        KPI Definitions → File Cache → Pre-calculated Results
```

## Tech Stack

### Core Components
- **Data Processing**: Pandas + DuckDB
- **Data Storage**: Parquet files + DuckDB (analytical queries)
- **Metadata Storage**: SQLite (user management, configurations)
- **API**: FastAPI
- **Caching**: File-based JSON caching
- **Frontend**: Streamlit + Plotly

### Future Additions (when needed)
- **Dask**: For parallel processing and memory optimization
- **Redis**: For faster caching and real-time features
- **PostgreSQL**: For complex relational data requirements

## Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vitaBI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Development

1. **Run the dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

2. **Run the API server**
   ```bash
   uvicorn api.main:app --reload
   ```

## Project Structure

```
vitaBI/
├── api/                    # FastAPI backend
├── dashboard/              # Streamlit dashboard
├── data_processor/         # Data processing pipeline
├── qlik_extractor/         # Qlik Sense data migration
├── tests/                  # Test files
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── PROJECT_ROADMAP.md     # Detailed project roadmap
└── README.md              # This file
```

## Development Phases

### Phase 1: Data Migration & Core Pipeline (Weeks 1-3)
- Qlik Sense data extraction (QRS API/QVD)
- CSV to Parquet conversion
- DuckDB setup and optimization
- KPI calculation engine

### Phase 2: API & Backend Development (Weeks 4-5)
- FastAPI application
- User authentication
- Query caching
- Data export functionality

### Phase 3: Dashboard Development (Weeks 6-8)
- Streamlit dashboard
- Custom visualizations
- Interactive filtering
- Mobile responsiveness

### Phase 4: Testing & Optimization (Weeks 9-10)
- Performance testing
- Data validation
- User acceptance testing

### Phase 5: Deployment & Go-Live (Weeks 11-12)
- Production deployment
- User migration
- Support and monitoring

## Performance Targets

- **Query Response**: 2-3 seconds for complex queries
- **Dashboard Load**: < 1 second for pre-calculated KPIs
- **Concurrent Users**: 20-30 users
- **Data Processing**: 10-30 minutes for monthly import
- **Memory Usage**: < 32GB for 170M rows

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support, please open an issue in the GitHub repository.

## Roadmap

See [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) for detailed development timeline and technical specifications.
