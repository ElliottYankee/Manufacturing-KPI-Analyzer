import argparse
import data_analyzer as da
import sys
from pathlib import Path
from visualizer import ManufacturingVisualizer


def print_kpi_summary(analyzer):
    """Print a concise summary of key KPIs"""
    print("\n" + "="*60)
    print("MANUFACTURING KPI SUMMARY")
    print("="*60)
    
    # Get key metrics
    oee = analyzer.calculate_oee()
    efficiency = analyzer.calculate_overall_efficiency()
    quality = analyzer.calculate_quality_metrics()
    downtime = analyzer.calculate_downtime_analysis()
    
    # Display in organized format
    print(f"\nOVERALL PERFORMANCE:")
    print(f"   OEE:              {oee['oee']:.1f}% ({get_performance_rating(oee['oee'])})")
    print(f"   Efficiency:       {efficiency['overall_efficiency']:.1f}%")
    print(f"   Total Production: {oee['total_production']:,} units")
    print(f"   Shifts Analyzed:  {oee['total_shifts_analyzed']}")
    
    print(f"\nOEE COMPONENTS:")
    print(f"   Availability:     {oee['availability']:.1f}%")
    print(f"   Performance:      {oee['performance']:.1f}%") 
    print(f"   Quality Rate:     {oee['quality_rate']:.1f}%")
    
    print(f"\nDOWNTIME & QUALITY:")
    print(f"   Total Downtime:   {downtime['total_downtime_hours']:.1f} hours")
    print(f"   Avg per Shift:    {downtime['average_downtime_per_shift_minutes']:.1f} minutes")
    print(f"   Quality Defects:  {quality['total_defects']:,} units ({quality['overall_defect_rate']:.2f}%)")
    
    # Top performers
    top_performers = analyzer.get_top_performers()
    print(f"\nTOP PERFORMERS:")
    print(f"   Best Machine:     {top_performers['top_machines'].index[0]} ({top_performers['top_machines'].iloc[0]:.1f}% OEE)")
    print(f"   Best Operator:    {top_performers['top_operators'].index[0]} ({top_performers['top_operators'].iloc[0]:.1f}% OEE)")


def get_performance_rating(oee_value):
    """Simple performance rating for OEE"""
    if oee_value >= 85:
        return "World Class"
    elif oee_value >= 75:
        return "Good"
    elif oee_value >= 65:
        return "Fair"
    else:
        return "Needs Improvement"


def run_visual_demo(analyzer):
    """Run the built-in visual demo"""
    print("\nVISUAL ANALYSIS DEMO")
    print("="*40)
    print("Creating comprehensive visual analysis of your manufacturing data...")
    print("Each chart will be displayed and saved to output/ folder")
    
    visualizer = ManufacturingVisualizer(analyzer)
    
    # Create visualizations with user interaction
    print("\n1/3 Creating OEE Overview Dashboard...")
    print("   Shows: OEE components, overall performance, machine comparison")
    input("   Press Enter to generate chart...")
    visualizer.plot_oee_overview()
    
    print("\n2/3 Creating Trend Analysis...")
    print("   Shows: OEE trends over time with performance benchmarks")
    input("   Press Enter to generate chart...")
    visualizer.plot_trends(metric='oee')
    
    print("\n3/3 Creating Machine Comparison...")
    print("   Shows: Performance comparison across all machines")
    input("   Press Enter to generate chart...")
    visualizer.plot_machine_comparison()
    
    print("\nVisual demo complete!")
    print("All charts saved to output/ folder")
    print("\nUse flags for specific analysis:")
    print("   --mode oee              (OEE analysis only)")
    print("   --mode efficiency       (Efficiency analysis)")  
    print("   --mode viz --chart trends   (Just trend chart)")


def run_specific_analysis(analyzer, mode, group_by=None, date_range=None):
    """Run specific analysis based on mode"""
    print(f"\n📊 Running {mode.upper()} Analysis...")
    print("-" * 40)
    
    try:
        if mode == "oee":
            results = analyzer.calculate_oee(group_by=group_by, date_range=date_range)
        elif mode == "efficiency":
            results = analyzer.calculate_overall_efficiency(group_by=group_by, date_range=date_range)
        elif mode == "throughput":
            results = analyzer.calculate_throughput_metrics(group_by=group_by, date_range=date_range)
        elif mode == "downtime":
            results = analyzer.calculate_downtime_analysis(group_by=group_by, date_range=date_range)
        elif mode == "quality":
            results = analyzer.calculate_quality_metrics(group_by=group_by, date_range=date_range)
        elif mode == "top":
            results = analyzer.get_top_performers(metric="oee")
        
        # Display results
        if isinstance(results, dict):
            for key, value in results.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print(results)
            
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")


def run_specific_visualization(analyzer, chart_type):
    """Run specific visualization"""
    visualizer = ManufacturingVisualizer(analyzer)
    
    print(f"\n🎨 Creating {chart_type.replace('_', ' ').title()}...")
    
    try:
        if chart_type == "overview":
            visualizer.plot_oee_overview()
        elif chart_type == "trends":
            visualizer.plot_trends(metric='oee')
        elif chart_type == "machines":
            visualizer.plot_machine_comparison()
        elif chart_type == "report":
            visualizer.create_summary_report()
        else:
            print(f"❌ Unknown chart type: {chart_type}")
            return
            
        print("✅ Visualization complete!")
        
    except Exception as e:
        print(f"❌ Error creating visualization: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        description="Manufacturing KPI Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=
        """
        Examples:
        python main.py                           # Default: Summary + Visual Demo
        python main.py --mode oee               # OEE analysis only  
        python main.py --mode efficiency --group-by machine_id
        python main.py --mode viz --chart overview
        python main.py --start 2024-01-01 --end 2024-01-31
        """
        )
    
    # Basic arguments
    parser.add_argument("--data", type=str, default="data/sample_data.csv",
                       help="Path to manufacturing data CSV")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)")
    
    # Analysis modes
    parser.add_argument("--mode", type=str, 
                       choices=["summary", "oee", "efficiency", "throughput", 
                               "downtime", "quality", "top", "viz"],
                       help="Analysis mode (default: summary with visual demo)")
    
    parser.add_argument("--group-by", type=str, 
                       choices=["machine_id", "shift", "operator_id"],
                       help="Group results by field")
    
    # Visualization options  
    parser.add_argument("--chart", type=str,
                       choices=["overview", "trends", "machines", "report"],
                       help="Specific chart type (use with --mode viz)")
    
    parser.add_argument("--no-demo", action="store_true",
                       help="Skip visual demo in default mode")
    
    args = parser.parse_args()
    
    # Welcome message
    print("🏭 Manufacturing KPI Analyzer")
    print("=" * 50)
    
    # Check data file exists
    if not Path(args.data).exists():
        print(f"❌ Data file not found: {args.data}")
        print("💡 Run 'python generate_sample_data.py' first")
        sys.exit(1)
    
    # Load data
    try:
        print(f"📁 Loading data from: {args.data}")
        analyzer = da.ManufacturingKPIAnalyzer(data_path=args.data)
        print(f"✅ Loaded {len(analyzer.df)} records")
        
        date_range_str = f"{analyzer.df['timestamp'].min().date()} to {analyzer.df['timestamp'].max().date()}"
        print(f"📅 Date range: {date_range_str}")
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        sys.exit(1)
    
    # Prepare date range
    date_range = (args.start, args.end) if args.start and args.end else None
    if date_range:
        print(f"🔍 Filtering to: {args.start} to {args.end}")
    
    # Run based on mode
    if args.mode == "viz":
        # Specific visualization
        if not args.chart:
            print("❌ --chart required with --mode viz")
            parser.print_help()
            sys.exit(1)
        run_specific_visualization(analyzer, args.chart)
        
    elif args.mode and args.mode != "summary":
        # Specific analysis mode
        run_specific_analysis(analyzer, args.mode, args.group_by, date_range)
        
    else:
        # Default mode: Summary + Visual Demo
        print_kpi_summary(analyzer)
        
        if not args.no_demo:
            print(f"\n🎨 Starting visual demo...")
            demo_choice = input("Run visual demo? (y/n, default=y): ").lower().strip()
            
            if demo_choice != 'n':
                run_visual_demo(analyzer)
        
    print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    main()