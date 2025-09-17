import pandas as pd
import numpy as np

class ManufacturingKPIAnalyzer:
    """
    Manufacturing KPI Calculator
    Calculates key performance indicators for manufacturing data
    Optimized for efficiency and clarity
    """
    
    def __init__(self, data_path='data/sample_data.csv'):
        """Initialize with manufacturing data"""
        self.df = pd.read_csv(data_path)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self._calculate_derived_metrics()
    
    def _calculate_derived_metrics(self):
        """Calculate derived metrics that will be used in multiple KPIs"""
        # Core calculations - calculate once, use multiple times
        shift_minutes = 480  # 8 hours = 480 minutes
        
        # Efficiency per record
        self.df['efficiency'] = (self.df['actual_production'] / 
                               self.df['target_production'] * 100).round(2)
        
        # Time-based metrics
        self.df['available_minutes'] = shift_minutes - self.df['downtime_minutes']
        self.df['availability'] = (self.df['available_minutes'] / shift_minutes * 100).round(2)
        
        # Performance ratio (actual vs adjusted target when available)
        self.df['performance'] = np.where(
            self.df['available_minutes'] > 0,
            (self.df['actual_production'] / 
             (self.df['target_production'] * np.maximum(self.df['available_minutes'] / shift_minutes, 0.001)) * 100),
            0
        ).round(2)
        
        # Quality rate (good units / total units)
        self.df['quality_rate'] = np.where(
            self.df['actual_production'] > 0,
            ((self.df['actual_production'] - self.df['quality_defects']) / 
             self.df['actual_production'] * 100),
            0
        ).round(2)
        
        # OEE calculation
        self.df['oee'] = (self.df['availability'] * self.df['performance'] * 
                         self.df['quality_rate'] / 10000).round(2)
    
    def calculate_overall_efficiency(self, group_by=None, date_range=None):
        """
        Calculate overall equipment efficiency
        Args:
            group_by: 'machine_id', 'shift', 'operator_id', or None for overall
            date_range: tuple of (start_date, end_date) as strings
        """
        df_filtered = self._filter_data(date_range)
        
        if group_by:
            result = df_filtered.groupby(group_by).agg({
                'actual_production': 'sum',
                'target_production': 'sum',
                'efficiency': 'mean'
            }).round(2)
            # Calculating true efficiency from totals (more accurate than average)
            result['calculated_efficiency'] = (result['actual_production'] / 
                                             result['target_production'] * 100).round(2)
            return result
        else:
            # Overall calculations - minimize operations
            total_actual = df_filtered['actual_production'].sum()
            total_target = df_filtered['target_production'].sum()
            
            return {
                'total_actual_production': total_actual,
                'total_target_production': total_target,
                'overall_efficiency': round(total_actual / total_target * 100, 2),
                'average_efficiency_per_shift': round(df_filtered['efficiency'].mean(), 2),
                'total_shifts_analyzed': len(df_filtered)
            }
    
    def calculate_oee(self, group_by=None, date_range=None):
        """
        Calculate Overall Equipment Effectiveness (OEE)
        OEE = Availability × Performance × Quality
        """
        df_filtered = self._filter_data(date_range)
        
        if group_by:
            result = df_filtered.groupby(group_by).agg({
                'availability': 'mean',
                'performance': 'mean', 
                'quality_rate': 'mean',
                'oee': 'mean',
                'actual_production': 'sum',
                'downtime_minutes': 'sum'
            }).round(2)
            # Add total downtime in hours for business context
            result['total_downtime_hours'] = (result['downtime_minutes'] / 60).round(1)
            return result
        else:
            # Optimizing overall OEE calculation
            total_shifts = len(df_filtered)
            total_possible_time = total_shifts * 480  # 480 minutes per shift
            total_available_time = total_possible_time - df_filtered['downtime_minutes'].sum()
            
            # Calculating OEE components
            overall_availability = total_available_time / total_possible_time * 100
            overall_performance = df_filtered['performance'].mean()
            overall_quality = df_filtered['quality_rate'].mean()
            overall_oee = overall_availability * overall_performance * overall_quality / 10000
            
            return {
                'availability': round(overall_availability, 2),
                'performance': round(overall_performance, 2),
                'quality_rate': round(overall_quality, 2),
                'oee': round(overall_oee, 2),
                'total_production': df_filtered['actual_production'].sum(),
                'total_downtime_hours': round((total_possible_time - total_available_time) / 60, 1),
                'total_shifts_analyzed': total_shifts,
                'utilization_days': (df_filtered['timestamp'].max() - df_filtered['timestamp'].min()).days + 1
            }
    
    def calculate_throughput_metrics(self, group_by=None, date_range=None):
        """Calculate throughput and cycle time metrics"""
        df_filtered = self._filter_data(date_range)
        
        if group_by:
            result = df_filtered.groupby(group_by).agg({
                'actual_production': ['sum', 'mean'],
                'available_minutes': 'sum'
            })
            # Flattening column names for easier access
            result.columns = ['total_production', 'avg_production_per_shift', 'total_available_minutes']
            result['throughput_per_hour'] = (result['total_production'] / 
                                           (result['total_available_minutes'] / 60)).round(2)
            return result
        else:
            # Optimizing calculations
            total_production = df_filtered['actual_production'].sum()
            total_available_minutes = df_filtered['available_minutes'].sum()
            total_available_hours = total_available_minutes / 60
            
            return {
                'total_production': total_production,
                'total_available_hours': round(total_available_hours, 1),
                'average_throughput_per_hour': round(total_production / total_available_hours, 2),
                'average_production_per_shift': round(df_filtered['actual_production'].mean(), 2),
                'peak_shift_production': df_filtered['actual_production'].max(),
                'total_shifts_analyzed': len(df_filtered)
            }
    
    def calculate_downtime_analysis(self, group_by=None, date_range=None):
        """Analyze downtime patterns"""
        df_filtered = self._filter_data(date_range)
        
        if group_by:
            result = df_filtered.groupby(group_by).agg({
                'downtime_minutes': ['sum', 'mean', 'max'],
                'availability': 'mean'
            }).round(2)
            result.columns = ['total_downtime_min', 'avg_downtime_min', 'max_downtime_min', 'avg_availability']
            # Converting to hours for business readability
            result['total_downtime_hours'] = (result['total_downtime_min'] / 60).round(1)
            return result
        else:
            # Single pass through data for all calculations
            downtime_data = df_filtered['downtime_minutes']
            total_downtime = downtime_data.sum()
            
            return {
                'total_downtime_hours': round(total_downtime / 60, 1),
                'average_downtime_per_shift_minutes': round(downtime_data.mean(), 1),
                'worst_downtime_shift_minutes': downtime_data.max(),
                'shifts_with_high_downtime': (downtime_data > 60).sum(),  # >1 hour - optimized boolean sum
                'shifts_with_zero_downtime': (downtime_data == 0).sum(),
                'overall_availability': round(df_filtered['availability'].mean(), 2),
                'total_shifts_analyzed': len(df_filtered)
            }
    
    def calculate_quality_metrics(self, group_by=None, date_range=None):
        """Calculate quality-related KPIs"""
        df_filtered = self._filter_data(date_range)
        
        if group_by:
            result = df_filtered.groupby(group_by).agg({
                'quality_defects': 'sum',
                'actual_production': 'sum',
                'quality_rate': 'mean'
            }).round(2)
            result['defect_rate'] = ((result['quality_defects'] / result['actual_production']) * 100).round(3)
            return result
        else:
            # Optimizing by calculating totals once
            total_defects = df_filtered['quality_defects'].sum()
            total_production = df_filtered['actual_production'].sum()
            quality_rates = df_filtered['quality_rate']
            
            return {
                'total_defects': total_defects,
                'total_production': total_production,
                'overall_defect_rate': round((total_defects / total_production) * 100, 3),
                'average_quality_rate': round(quality_rates.mean(), 2),
                'best_quality_shift': round(quality_rates.max(), 2),
                'worst_quality_shift': round(quality_rates.min(), 2),
                'quality_consistency_std': round(quality_rates.std(), 2),
                'total_shifts_analyzed': len(df_filtered)
            }
    
    def get_top_performers(self, metric='oee', top_n=3):
        """Get top performing machines/operators by specified metric"""
        # Validate metric parameter
        valid_metrics = ['oee', 'efficiency', 'quality_rate', 'availability', 'performance']
        if metric not in valid_metrics:
            raise ValueError(f"Metric must be one of: {valid_metrics}")
        
        # Single groupby operation for both machine and operator rankings
        by_machine = self.df.groupby('machine_id')[metric].mean().sort_values(ascending=False)
        by_operator = self.df.groupby('operator_id')[metric].mean().sort_values(ascending=False)
        
        return {
            'top_machines': by_machine.head(top_n).round(2),
            'top_operators': by_operator.head(top_n).round(2),
            'metric_analyzed': metric,
            'total_machines': len(by_machine),
            'total_operators': len(by_operator)
        }
    
    def _filter_data(self, date_range):
        """Helper method to filter data by date range"""
        if date_range is None:
            return self.df
        
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        return self.df[(self.df['timestamp'] >= start_date) & (self.df['timestamp'] <= end_date)]
    
    def get_summary_report(self, date_range=None):
        """Generate a comprehensive summary report"""
        df_filtered = self._filter_data(date_range)
        
        # Calculating date range info once
        date_min, date_max = df_filtered['timestamp'].min(), df_filtered['timestamp'].max()
        
        report = {
            'data_overview': {
                'total_records': len(df_filtered),
                'date_range': (date_min.strftime('%Y-%m-%d'), date_max.strftime('%Y-%m-%d')),
                'analysis_days': (date_max - date_min).days + 1,
                'machines': sorted(df_filtered['machine_id'].unique().tolist()),
                'operators': sorted(df_filtered['operator_id'].unique().tolist()),
                'shifts_analyzed': df_filtered['shift'].value_counts().to_dict()
            },
            'overall_kpis': self.calculate_oee(date_range=date_range),
            'efficiency': self.calculate_overall_efficiency(date_range=date_range),
            'throughput': self.calculate_throughput_metrics(date_range=date_range),
            'downtime': self.calculate_downtime_analysis(date_range=date_range),
            'quality': self.calculate_quality_metrics(date_range=date_range),
            'top_performers': self.get_top_performers()
        }
        return report
    
    def get_machine_comparison(self, metric='oee', date_range=None):
        """Compare all machines on a specific metric"""
        df_filtered = self._filter_data(date_range)
        
        comparison = df_filtered.groupby('machine_id').agg({
            'oee': 'mean',
            'efficiency': 'mean',
            'availability': 'mean',
            'performance': 'mean',
            'quality_rate': 'mean',
            'actual_production': 'sum',
            'downtime_minutes': 'sum'
        }).round(2)
        
        # Adding derived metrics
        comparison['total_downtime_hours'] = (comparison['downtime_minutes'] / 60).round(1)
        comparison['shifts_operated'] = df_filtered.groupby('machine_id').size()
        
        # Sorting by specified metric
        comparison = comparison.sort_values(metric, ascending=False)
        
        return comparison
    
    def get_trend_analysis(self, metric='oee', group_by='timestamp', date_range=None):
        """Analyze trends over time"""
        df_filtered = self._filter_data(date_range)
        
        if group_by == 'timestamp':
            # Grouping by date for daily trends
            df_filtered['date'] = df_filtered['timestamp'].dt.date
            trend_data = df_filtered.groupby('date')[metric].mean().round(2)
        else:
            trend_data = df_filtered.groupby(group_by)[metric].mean().round(2)
        
        return {
            'trend_data': trend_data,
            'trend_direction': 'improving' if trend_data.iloc[-1] > trend_data.iloc[0] else 'declining',
            'best_period': trend_data.idxmax(),
            'worst_period': trend_data.idxmin(),
            'average_value': round(trend_data.mean(), 2),
            'volatility': round(trend_data.std(), 2)
        }

# Convenience function for quick analysis
def quick_analysis(data_path='data/sample_data.csv', date_range=None):
    """Quick analysis function for easy use"""
    analyzer = ManufacturingKPIAnalyzer(data_path)
    return analyzer.get_summary_report(date_range=date_range)