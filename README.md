# Manufacturing-KPI-Analyzer

A comprehensive Python tool for analyzing manufacturing performance data with automated KPI calculations and professional visualizations. Built as a learning project to demonstrate data analysis, visualization, and software engineering best practices.


<br>
\## Project Overview

This tool transforms raw manufacturing data into actionable insights through:
 \- Automated KPI Calculations - OEE, efficiency, quality, throughput, and downtime analysis
 \- Professional Visualizations - Interactive charts and dashboards using matplotlib
 \- Flexible Analysis Options - Command-line interface with multiple analysis modes


<br>
\## Personal Motivation

I wanted to further hone my data analysis in a manufacturing setting. 


<br>
\## Setup

1\. Clone the repository

2\. Create virtual environment: `python -m venv venv`

3\. Activate environment: `source venv/bin/activate` (Mac/Linux) or `venv\\Scripts\\activate` (Windows)

4\. Install dependencies: `pip install -r requirements.txt`

5\. Generate Sample Data: `python generate_sample_data.py`

5\. Quick Start: `python main.py`


<br>
\## Usage
\* Quick Start (recommended): 
 \- `python main.py`                                                 # Runs the full interactive demo with KPI summary and all visualizations

\* Analysis Modes
 \- `python main.py --mode oee`                                      # OEE analysis only
 \- `python main.py --mode efficiency`                               # Production efficiency
 \- `python main.py --mode quality`                                  # Quality metrics
 \- `python main.py --mode downtime`                                 # Downtime analysis
 \- `python main.py --mode top`                                      # Top performers

\* Visualizations Only
 \- `python main.py --mode viz --chart overview`                     # OEE dashboard
 \- `python main.py --mode viz --chart trends`                       # Trend analysis
 \- `python main.py --mode viz --chart machines`                     # Machine comparison
 \- `python main.py --mode viz --chart report`                       # All visualizations

\* Data Filtering & Grouping
 \- `python main.py --mode oee --group-by machine_id`                # OEE by machine
 \- `python main.py --mode efficiency --group-by shift`              # Efficiency by shift
 \- `python main.py --start 2024-01-01 --end 2024-01-31`             # Date range filter
 \- `python main.py --data my_data.csv --mode viz --chart overview`  # Custom data file


<br>
\## Features

\* Core Analytics
 \- Overall Equipment Effectiveness (OEE): Industry-standard calculation with availability, performance, and quality components
 \- Production Efficiency: Actual vs target production analysis
 \- Quality Metrics: Defect rates, quality consistency, and performance classification
 \- Downtime Analysis: Patterns, trends, and root cause identification
 \- Throughput Analysis: Production rates and capacity utilization
 \- Performance Rankings: Top performing machines and operators

\* Visualizations
 \- OEE Dashboard: 4-panel comprehensive overview with gauges and comparisons
 \- Trend Analysis: Time-series charts with benchmark lines and trend indicators
 \- Machine Comparison: Multi-metric performance comparison across equipment
 \- Executive Summary: High-level KPI cards with automated insights

\* Technical Attributes
 \- Flexible Data Input: CSV file support with data validation
 \- Date Filtering: Analyze specific time periods
 \- Grouping Options: Results by machine, shift, or operator
 \- Export Capabilities: High-quality chart exports to PNG
 \- Memory Optimization: Efficient data processing for large datasets


<br>
\## Project Structure

Manufacturing-KPI-Analyzer/
├── main.py                   # Entry point with CLI interface<br>
├── data\_analyzer.py         # Core KPI calculation engine<br>
├── visualizer.py             # Matplotlib chart generation<br>
├── generate_sample_data.py   # Sample data generation<br>
├── requirements.txt          # Python dependencies<br>
├── README.md                 # This file<br>
├── data/                     <br>
│   └── sample_data.csv       # Generated sample manufacturing data<br>
└── output/                   # Generated charts and reports<br>
    ├── oee_overview_*.png<br>
    ├── trends_*.png<br>
    └── machine_comparison_*.png
