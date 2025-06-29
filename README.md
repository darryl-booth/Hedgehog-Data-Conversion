# Hedgehog Data Conversion

This project contains a simple Flask application configured to use HTMX, Pandas, and Flask Sessions. Credentials such as `SECRET_KEY` should be provided via environment variables or a `.env` file (excluded from version control).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the development server with:

```bash
python run.py
```

Run the tests with:

```bash
pytest
```

