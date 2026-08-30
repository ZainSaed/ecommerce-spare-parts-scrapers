# E-commerce Spare Parts Scrapers

A Python-based web scraping system for extracting and structuring spare-part data from e-commerce websites.

Built initially for **Breville Australia** and **Electrolux Australia**.

## What It Does

* Discovers product and spare-part categories
* Finds model-specific parts pages
* Extracts spare-part URLs
* Collects SKUs, names, prices, and availability
* Detects compatible product models
* Removes duplicate parts
* Separates spare parts from accessories and excluded products
* Creates part-to-model relationships
* Exports structured CSV files

## Workflow

```text
Website
   ↓
Category Discovery
   ↓
Parts Discovery
   ↓
Product Extraction
   ↓
Classification
   ↓
Deduplication
   ↓
CSV Dataset
```

## Tech Stack

* Python
* Playwright
* Web Scraping
* Data Processing
* CSV

## Output

```text
spare_parts.csv
excluded_products.csv
part_models.csv
failed_pages.csv
```

## Use Cases

* E-commerce research
* Spare-part catalog creation
* Product matching
* Price monitoring
* Inventory analysis
* Automation pipelines

## Disclaimer

For educational and authorized data-integration purposes. Respect the target website's terms, rate limits, and applicable policies.
