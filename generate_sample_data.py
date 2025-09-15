import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_manufacturing_data(days=30, machines=6):
    """Generate realistic manufacturing data"""
    
    # Set random seed for reproducible data
    np.random.seed(1)
    random.seed(1)
    
    # Machine configurations
    machines_config = {
        'A1': {'target_rate': 100, 'reliability': 0.95},  # High performer
        'A2': {'target_rate': 100, 'reliability': 0.88},  # Average
        'B1': {'target_rate': 85, 'reliability': 0.92},   # Older machine
        'B2': {'target_rate': 85, 'reliability': 0.85},   # Problem machine
        'C1': {'target_rate': 120, 'reliability': 0.93},  # New machine
        'C2': {'target_rate': 120, 'reliability': 0.90}   # New machine
    }
    
    # Operators and shifts
    operators = ['OP001', 'OP002', 'OP003', 'OP004', 'OP005', 'OP006']
    shifts = ['Morning', 'Afternoon', 'Night']
    #shift_hours = {'Morning': (6, 14), 'Afternoon': (14, 22), 'Night': (22, 6)}
    
    data = []
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # Skip weekends (optional - comment out if 24/7 operation)
        if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            continue
            
        for shift in shifts:
            for machine_id, config in machines_config.items():
                
                # Shift-based variations
                if shift == 'Night':
                    performance_factor = 0.85  # Night shift typically lower
                elif shift == 'Morning':
                    performance_factor = 1.0   # Best performance
                else:
                    performance_factor = 0.95  # Afternoon slight dip
                
                # Random operator assignment
                operator = random.choice(operators)
                
                # Calculate production metrics
                target_production = config['target_rate'] * 8  # 8-hour shift
                
                # Add realistic variability
                efficiency = (config['reliability'] * performance_factor * 
                            np.random.normal(1.0, 0.1))  # ±10% variation
                efficiency = max(0.3, min(1.2, efficiency))  # Keep reasonable bounds
                
                actual_production = int(target_production * efficiency)
                
                # Calculate downtime (inversely related to efficiency)
                base_downtime = (1 - config['reliability']) * 480  # 480 minutes in 8 hours
                downtime_minutes = max(0, int(base_downtime + np.random.normal(0, 20)))
                
                # Quality defects (typically 1-5% of production)
                defect_rate = np.random.uniform(0.01, 0.05)
                quality_defects = int(actual_production * defect_rate)
                
                # Create timestamp for the shift
                if shift == 'Morning':
                    timestamp = current_date.replace(hour=6, minute=0, second=0)
                elif shift == 'Afternoon':
                    timestamp = current_date.replace(hour=14, minute=0, second=0)
                else:  # Night
                    timestamp = current_date.replace(hour=22, minute=0, second=0)
                
                data.append({
                    'timestamp': timestamp,
                    'machine_id': machine_id,
                    'operator_id': operator,
                    'shift': shift,
                    'target_production': target_production,
                    'actual_production': actual_production,
                    'downtime_minutes': downtime_minutes,
                    'quality_defects': quality_defects,
                    'setup_time_minutes': np.random.randint(15, 45),  # Setup time
                    'material_waste_kg': np.random.uniform(2.0, 8.0),  # Material waste
                })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Generate the data
    print("🏭 Generating manufacturing data...")
    df = generate_manufacturing_data(days=30, machines=6)
    print("🏭 Printing manufacturing data...")
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
        
    print("🔍 MANUFACTURING DATA OVERVIEW")
    print("=" * 50)
    print(f"Total Records: {len(df)}")
    print(f"Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Machines: {', '.join(df['machine_id'].unique())}")
    print(f"Operators: {', '.join(df['operator_id'].unique())}")
    print(f"Shifts: {', '.join(df['shift'].unique())}")
    
    print("\nPRODUCTION SUMMARY")
    print("=" * 30)
    print(f"Total Target Production: {df['target_production'].sum():,} units")
    print(f"Total Actual Production: {df['actual_production'].sum():,} units")
    print(f"Total Downtime: {df['downtime_minutes'].sum():,} minutes")
    print(f"Total Defects: {df['quality_defects'].sum():,} units")
    
    print(f"\nOverall Efficiency: {(df['actual_production'].sum() / df['target_production'].sum() * 100):.1f}%")
    
    print("\nBY MACHINE:")
    machine_summary = df.groupby('machine_id').agg({
        'actual_production': 'sum',
        'target_production': 'sum',
        'downtime_minutes': 'sum'
    })
    machine_summary['efficiency_%'] = (machine_summary['actual_production'] / 
                                        machine_summary['target_production'] * 100)
    print(machine_summary.round(1))
    
    print("\nFIRST 5 RECORDS:")
    print(df.head())
    
    # Save to CSV
    df.to_csv('data/sample_data.csv', index=False)

    print(f"\n💾 Saved to: data/sample_data.csv")