import argparse
import data_analyzer as da

def main():
    # --- Step 1: Parse CLI arguments for flexibility ---
    parser = argparse.ArgumentParser(description="Manufacturing KPI Analysis Tool")
    parser.add_argument(
        "--data", 
        type=str, 
        default="data/sample_data.csv", 
        help="Path to the manufacturing data CSV"
    )
    parser.add_argument(
        "--start", 
        type=str, 
        default=None, 
        help="Start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end", 
        type=str, 
        default=None, 
        help="End date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--mode", 
        type=str, 
        default="summary", 
        choices=["summary", "oee", "efficiency", "throughput", "downtime", "quality", "top"],
        help="Type of analysis to run"
    )
    args = parser.parse_args()

    # --- Step 2: Create analyzer instance ---
    analyzer = da.ManufacturingKPIAnalyzer(data_path=args.data)

    # --- Step 3: Build optional date range ---
    date_range = (args.start, args.end) if args.start and args.end else None

    # --- Step 4: Run the chosen analysis mode ---
    if args.mode == "summary":
        results = analyzer.get_summary_report(date_range=date_range)
    elif args.mode == "oee":
        results = analyzer.calculate_oee(date_range=date_range)
    elif args.mode == "efficiency":
        results = analyzer.calculate_overall_efficiency(date_range=date_range)
    elif args.mode == "throughput":
        results = analyzer.calculate_throughput_metrics(date_range=date_range)
    elif args.mode == "downtime":
        results = analyzer.calculate_downtime_analysis(date_range=date_range)
    elif args.mode == "quality":
        results = analyzer.calculate_quality_metrics(date_range=date_range)
    elif args.mode == "top":
        results = analyzer.get_top_performers(metric="oee")

    # --- Step 5: Pretty-print results ---
    print("\n===== KPI Analysis Results =====")
    if isinstance(results, dict):
        for k, v in results.items():
            print(f"{k}: {v}")
    else:
        # pandas DataFrame output
        print(results)

if __name__ == "__main__":
    main()