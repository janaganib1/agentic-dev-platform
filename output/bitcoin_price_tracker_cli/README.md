# Bitcoin Price CLI

A simple command-line tool to fetch and display the current Bitcoin price in USD.

## Features

- Fetches real-time Bitcoin price
- Formats price as USD currency with proper formatting
- Uses only Python standard library

## Installation

No dependencies required - uses Python standard library only.

```bash
# Install (no dependencies needed)
pip install -r requirements.txt
```

## Usage

Run the CLI to display current Bitcoin price:

```bash
python -m src.main
```

Example output:
```
Current Bitcoin Price: $45,123.45
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Project Structure

```
src/
  __init__.py        # Empty package file
  main.py            # CLI entry point
  config.py          # Configuration constants
  price_fetcher.py   # Bitcoin price fetcher
tests/
  __init__.py        # Empty package file
  test_main.py       # Basic tests
requirements.txt     # Empty (standard library only)
README.md           # This file
.env.example        # Environment variables template