🛒 Product Data Pipeline & Scraper – Data Engineering Project
📌 Overview

This project implements a reproducible data pipeline for collecting, structuring, and versioning product data from the Open Food Facts API.

It addresses real-world data engineering challenges such as:

Handling unreliable APIs (e.g. 503 errors)
Structuring raw data consistently
Ensuring dataset reproducibility
Separating code versioning (Git) from data versioning (DVC)

The pipeline follows a standard architecture:

RAW → INTERIM → PROCESSED

🎯 Objectives
Build a scalable data ingestion pipeline
Apply best practices in data organization
Ensure full reproducibility of datasets
Prepare data for analytics and machine learning use cases

🧰 Tech Stack
Python
aiohttp (asynchronous API requests)
Git & GitHub (code versioning)
DVC (Data Version Control) (data versioning)

📁 Project Structure
bidabi-clone-alone/
│
├── .dvc/
├── data/
│   ├── raw/
│   │   ├── images/
│   │   │   └── <category>/
│   │   └── metadata_<category>_<count>.csv
│   ├── interim/
│   ├── processed/
│   └── localstore/
│
├── src/
│   └── asyscrapper.py
│
├── raw.dvc
├── .gitignore
├── README.md
├── requirements.txt

⚙️ Data Pipeline
1. Data Ingestion (RAW)
Data is collected from the Open Food Facts API
Images are downloaded and grouped by category
Metadata is stored in CSV format

Example:

data/raw/images/milk/
data/raw/metadata_milk_180.csv
2. Data Organization

The pipeline enforces strict separation between stages:

Layer	Description
RAW	Original, unmodified data
INTERIM	Cleaned and transformed data
PROCESSED	Final dataset ready for modeling


⚠️ Handling Real-World Issues

This project accounts for real-world constraints:

API errors (e.g. HTTP 503)
Missing or broken image links
Incomplete or sparse product categories

Solutions implemented:

Robust error handling
Retry-friendly scraping logic
Flexible category-based ingestion


🔄 Data Versioning with DVC

Large datasets are not stored in Git.

Instead:

Git tracks code and .dvc files
DVC tracks actual data (images & CSVs)

📊 Dataset

Example categories collected:

sugar
milk
bread

Each category includes:

Product images
Structured metadata (CSV)


🧠 Key Learnings
Designing a modular data pipeline
Managing data vs code versioning (Git vs DVC)
Working with real-world imperfect APIs
Structuring projects for scalability and reuse


📌 Version History
v1.0 → Project setup
v2.0 → Scraper + RAW pipeline
v2.1 → DVC integration


👩‍💻 Author
Salma ALAOUI MRANI
Master Big Data & Business Intelligence
Université Sorbonne Paris Nord
