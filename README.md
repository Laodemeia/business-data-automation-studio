# Business Data Automation Studio

A bilingual Windows desktop application for cleaning, validating, filtering,
and exporting business data without requiring Microsoft Excel.

The project is designed for practical CSV, TXT, and XLSX workflows that would
otherwise require repetitive manual work. All processing happens locally on
the user's computer.

## Highlights

- Modern CustomTkinter interface with soft colors, rounded components, and
  animated selection panels
- English and Turkish interface
- CSV, delimited TXT, and XLSX import
- Multi-sheet Excel workbook support
- Automatic encoding and delimiter detection
- Source and processed-data previews
- Whitespace cleanup and column-name normalization
- Empty-row and duplicate-row removal
- Required-column and required-value validation
- Reusable filters and column renaming
- CSV, JSON, and formatted XLSX export
- Excel summary and validation-report sheets
- Reusable workflow profiles saved as JSON
- Local processing with no external data upload

## Quick Start on Windows

1. Install [Python 3](https://www.python.org/downloads/).
2. Download or clone this repository.
3. Run `KURULUM.bat` once.
4. Run `BASLAT.bat` whenever you want to open the application.

If startup fails, the launcher displays an error message and creates
`startup_error.log` in the project folder.

## Run from a Terminal

```bash
python -m pip install -r requirements.txt
python data_tools/business_data_studio.py
```

Microsoft Excel is not required. XLSX support is provided by `openpyxl`.

## Try the Example Workflows

The `examples` folder contains ready-to-use test files:

- `01_siparisler_kirli.csv` — inconsistent order data
- `02_stok_listesi.txt` — delimited inventory data
- `03_hazir_is_akisi.json` — saved workflow profile
- `04_cok_sayfali_siparisler.xlsx` — multi-sheet Excel workbook
- `TEST_REHBERI.md` — step-by-step Turkish test guide

A smaller CSV sample is also available at
`data_tools/sample_data/orders_dirty.csv`.

## Tests

Run the automated test suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

## Project Structure

```text
business-data-automation-studio/
├── BASLAT.bat
├── KURULUM.bat
├── requirements.txt
├── data_tools/
│   ├── business_data_studio.py
│   ├── business_data_studio/
│   │   ├── app.py
│   │   ├── engine.py
│   │   ├── translations.py
│   │   └── assets/icons/
│   └── sample_data/
├── examples/
└── tests/
```

## Current Scope

The current release focuses on structured CSV, delimited TXT, and XLSX
workflows. Old binary `.xls` files and VBA macros are not supported.
Multi-file batch processing and calculated-column workflows are possible
future additions.

## License

This project is available under the [MIT License](LICENSE). The interface uses
icons from [Lucide](https://lucide.dev/); see the included Lucide license file
for details.
