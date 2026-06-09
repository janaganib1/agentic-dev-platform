# Project Summary: bitcoin_price_tracker

**Generated:** 2026-06-04 11:35:44
**Complexity:** MEDIUM
**Original Requirement:** Develop a simple Bitcoin price tracker

Create a CLI application that fetches the current Bitcoin price in USD using the CoinGecko public API (no API key needed) and displays it to the user.
**Project Summary:** A CLI application that fetches and displays current Bitcoin price in USD using the CoinGecko API.
**Project Folder:** `output\bitcoin_price_tracker`

---

## Stories Completed: 3/3

### Story 1: Bitcoin price fetcher — ✅ DONE

**Requirement:** Create a function that fetches Bitcoin price data from the CoinGecko API and returns the USD price as a float.

**Acceptance Criteria:**
- Core function returns correct Bitcoin price as float for valid API response

**QA Status:** PASS
**Tech Stack:** See requirements.txt

---

### Story 2: Price display formatter — ✅ DONE

**Requirement:** Create a function that takes a Bitcoin price float and formats it as a readable string with currency symbol and proper decimal places.

**Acceptance Criteria:**
- Function formats price float into readable USD string with $ symbol and 2 decimal places

**QA Status:** PASS
**Tech Stack:** See requirements.txt

---

### Story 3: CLI interface — ✅ DONE

**Requirement:** Create a CLI script that calls the price fetcher and displays the formatted Bitcoin price to the user.

**Acceptance Criteria:**
- Running python -m src.main displays current Bitcoin price in USD format

**QA Status:** PASS
**Tech Stack:** See requirements.txt

---

## How to Run

```bash
cd output\bitcoin_price_tracker
pip install -r requirements.txt
py -m src.main <your_arguments>
```

## Notes for Jira

- Total stories implemented: 3
- All stories are in folder: `output\bitcoin_price_tracker`
- Each story's code is in `src/` subfolder
- Tests are in `tests/` subfolder
