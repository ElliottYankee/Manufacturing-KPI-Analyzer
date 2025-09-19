import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Setting professional styling
plt.style.use('default')
sns.set_palette("husl")

# Configuring matplotlib for better screen display
plt.rcParams['figure.max_open_warning'] = 50
plt.rcParams['figure.dpi'] = 100  # Good balance for screen display
plt.rcParams['savefig.dpi'] = 300  # High quality for saved files

class ManufacturingVisualizer:
    
    def __init__(self, analyzer, output_dir='output'):
        """
        Initialize visualizer
        
        Args:
            analyzer: ManufacturingKPIAnalyzer instance
            output_dir: Directory to save charts
        """
        self.analyzer = analyzer
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Simple color scheme
        self.colors = {
            'excellent': '#4CAF50',   # Green - World class (85%+)
            'good': '#8BC34A',        # Light green - Good (75-84%)
            'fair': '#FFC107',        # Yellow - Fair (65-74%) 
            'poor': '#FF5722',        # Red - Poor (<65%)
            'primary': '#2196F3',     # Blue - Default bars/lines
            'secondary': '#FF9800',   # Orange - Secondary elements
            'trend': '#9C27B0',       # Purple - For trend lines (distinct from orange)
            'target_good': '#4CAF50', # Green for good targets
            'target_fair': '#FF9800'  # Orange for fair targets
        }
    
    def get_performance_color(self, value):
        """
        Simple function to get color based on performance value
        """
        if value >= 85:
            return self.colors['excellent']
        elif value >= 75:
            return self.colors['good']
        elif value >= 65:
            return self.colors['fair']
        else:
            return self.colors['poor']
    
    def plot_oee_overview(self, save=True):
        """
        Create main OEE overview dashboard
        """
        # Getting the needed data
        oee_data = self.analyzer.calculate_oee()
        machine_oee = self.analyzer.calculate_oee(group_by='machine_id')
        
        # Creating 2x2 subplot layout
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Manufacturing OEE Overview', fontsize=16, fontweight='bold')
        
        # Chart 1: OEE Components (Horizontal Bar Chart)
        components = ['Availability', 'Performance', 'Quality Rate']
        values = [oee_data['availability'], oee_data['performance'], oee_data['quality_rate']]
        colors = [self.get_performance_color(v) for v in values]
        
        bars = ax1.barh(components, values, color=colors, alpha=0.8)
        ax1.set_xlim(0, 105)
        ax1.set_xlabel('Percentage (%)')
        ax1.set_title('OEE Components')
        
        # Adding value labels for readability
        for bar, value in zip(bars, values):
            ax1.text(bar.get_width() - 5, bar.get_y() + bar.get_height()/2, 
                    f'{value:.1f}%', va='center', ha='right', fontweight='bold', color='white')
        
        # Chart 2: Overall OEE (Simple gauge-style)
        oee_value = oee_data['oee']
        
        # Creating a simple "gauge" using a pie chart
        sizes = [oee_value, 100 - oee_value]
        colors_gauge = [self.get_performance_color(oee_value), 'lightgray']
        
        wedges, texts = ax2.pie(sizes, colors=colors_gauge, startangle=90, counterclock=False)
        
        # Adding center text
        ax2.text(0, 0, f'{oee_value:.1f}%\nOEE', ha='center', va='center', 
                fontsize=20, fontweight='bold')
        ax2.set_title('Overall OEE')
        
        # Chart 3: OEE by Machine (Vertical Bar Chart)
        machines = machine_oee.index.tolist()
        machine_values = machine_oee['oee'].values
        machine_colors = [self.get_performance_color(v) for v in machine_values]
        
        bars = ax3.bar(machines, machine_values, color=machine_colors, alpha=0.8)
        ax3.set_ylabel('OEE (%)')
        ax3.set_xlabel('Machine ID')
        ax3.set_title('OEE by Machine')
        ax3.set_ylim(0, 100)
        
        # Adding benchmark lines to show target performance
        ax3.axhline(85, color=self.colors['target_good'], linestyle='--', alpha=0.8, label='World Class (85%)')
        ax3.axhline(75, color=self.colors['target_fair'], linestyle='--', alpha=0.8, label='Good (75%)')
        ax3.legend(fontsize=9, loc='upper right')
        
        # Adding value labels on bars
        for bar, value in zip(bars, machine_values):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Chart 4: Production Efficiency
        efficiency_data = self.analyzer.calculate_overall_efficiency(group_by='machine_id')
        actual = efficiency_data['actual_production'].values
        target = efficiency_data['target_production'].values
        
        x = np.arange(len(machines))
        width = 0.35
        
        ax4.bar(x - width/2, target, width, label='Target', color='lightblue', alpha=0.7)
        ax4.bar(x + width/2, actual, width, label='Actual', color=self.colors['primary'], alpha=0.8)
        
        ax4.set_ylabel('Production Units')
        ax4.set_xlabel('Machine ID')
        ax4.set_title('Production: Target vs Actual')
        ax4.set_xticks(x)
        ax4.set_xticklabels(machines)
        ax4.legend()
        
        # Adjusting layout to prevent overlap
        plt.tight_layout()
        
        # Saving if requested
        if save:
            filename = f"oee_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved: {filepath}")
        
        plt.show()
        return fig
    
    def plot_trends(self, metric='oee', days=30, save=True):
        """
        Simple trend analysis over time
        """
        # Preparing time-series data
        df = self.analyzer.df.copy()
        df['date'] = df['timestamp'].dt.date  # Extracting just the date
        
        # Grouping by date and calculating daily averages
        daily_data = df.groupby('date')[metric].mean()
        
        # Limiting to recent days if specified
        if days and len(daily_data) > days:
            daily_data = daily_data.tail(days)
        
        # Creating the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plotting main trend line
        ax.plot(daily_data.index, daily_data.values, 
               marker='o', linewidth=2, markersize=4, color=self.colors['primary'])
        
        # Adding trend line using numpy polyfit to show mathematical concepts
        x_numeric = np.arange(len(daily_data))
        trend_coeffs = np.polyfit(x_numeric, daily_data.values, 1)  # Linear trend
        trend_line = np.poly1d(trend_coeffs)
        
        ax.plot(daily_data.index, trend_line(x_numeric), 
               linestyle='--', color=self.colors['primary'], alpha=0.8, 
               label=f'Trend (slope: {trend_coeffs[0]:.2f})')
        
        # Formatting
        ax.set_title(f'{metric.upper()} Trend Analysis (Last {len(daily_data)} days)', fontsize=14, fontweight='bold')
        ax.set_ylabel(f'{metric.upper()} (%)')
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Rotating x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Adding benchmark line for OEE
        if metric == 'oee':
            ax.axhline(85, color=self.colors['target_good'], linestyle=':', alpha=0.8, linewidth=5, label='World Class Target')
            ax.axhline(75, color=self.colors['target_fair'], linestyle=':', alpha=0.8, linewidth=5, label='Good Target')
            ax.legend()
        
        plt.tight_layout()
        
        if save:
            filename = f"{metric}_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"📈 Saved: {filepath}")
        
        plt.show()
        return fig
    
    def plot_machine_comparison(self, save=True):
        """
        Compare all machines across key metrics
        """
        # Getting machine data
        machine_data = self.analyzer.get_machine_comparison()
        machines = machine_data.index.tolist()
        
        # Creating 2x2 subplot for key metrics
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Machine Performance Comparison', fontsize=16, fontweight='bold')
        
        # Metric 1: OEE
        oee_values = machine_data['oee'].values
        colors_oee = [self.get_performance_color(v) for v in oee_values]
        
        bars1 = ax1.bar(machines, oee_values, color=colors_oee, alpha=0.8)
        ax1.set_title('OEE by Machine')
        ax1.set_ylabel('OEE (%)')
        ax1.set_xlabel('Machine ID')
        ax1.set_ylim(0, 100)
        ax1.axhline(85, color=self.colors['target_good'], linestyle='--', alpha=0.8, linewidth=5, label='World Class (85%)')
        ax1.axhline(75, color=self.colors['target_fair'], linestyle='--', alpha=0.8, linewidth=5, label='Good (75%)')
        ax1.legend(fontsize=9)
        
        # Adding value labels - reusable pattern
        for bar, value in zip(bars1, oee_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Metric 2: Availability
        avail_values = machine_data['availability'].values
        colors_avail = [self.get_performance_color(v) for v in avail_values]
        
        bars2 = ax2.bar(machines, avail_values, color=colors_avail, alpha=0.8)
        ax2.set_title('Availability by Machine')
        ax2.set_ylabel('Availability (%)')
        ax2.set_xlabel('Machine ID')
        ax2.set_ylim(0, 100)
        
        for bar, value in zip(bars2, avail_values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Metric 3: Quality Rate
        quality_values = machine_data['quality_rate'].values
        
        bars3 = ax3.bar(machines, quality_values, color=self.colors['excellent'], alpha=0.8)
        ax3.set_title('Quality Rate by Machine')
        ax3.set_ylabel('Quality Rate (%)')
        ax3.set_xlabel('Machine ID')
        ax3.set_ylim(90, 100)  # Zoom in on quality range
        ax3.axhline(95, color=self.colors['poor'], linestyle='--', alpha=0.8, linewidth=5, label='Target (95%)')
        ax3.legend()
        
        for bar, value in zip(bars3, quality_values):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Metric 4: Total Production
        prod_values = machine_data['actual_production'].values
        
        bars4 = ax4.bar(machines, prod_values, color=self.colors['primary'], alpha=0.8)
        ax4.set_title('Total Production by Machine')
        ax4.set_ylabel('Total Units Produced')
        ax4.set_xlabel('Machine ID')
        
        for bar, value in zip(bars4, prod_values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(prod_values)*0.01,
                    f'{value:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            filename = f"machine_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"🏭 Saved: {filepath}")
        
        plt.show()
        return fig
    
    def create_summary_report(self, save=True):
        """
        Create a simple summary report with key insights
        """
        print("📋 Generating Manufacturing Summary Report...")
        
        # Creating multiple charts
        print("1/3 Creating OEE Overview...")
        self.plot_oee_overview(save=save)
        
        print("2/3 Creating Trend Analysis...")
        self.plot_trends(metric='oee', save=save)
        
        print("3/3 Creating Machine Comparison...")
        self.plot_machine_comparison(save=save)
        
        print("✅ Summary report complete!")
        print(f"📁 All files saved to: {self.output_dir}")
        
        return True


# Convenience functions for easy use
def quick_overview(data_path='data/sample_data.csv'):
    """One function call OEE overview"""
    from data_analyzer import ManufacturingKPIAnalyzer
    
    analyzer = ManufacturingKPIAnalyzer(data_path)
    visualizer = ManufacturingVisualizer(analyzer)
    return visualizer.plot_oee_overview()


def quick_trends(data_path='data/sample_data.csv', metric='oee'):
    """One function call trend analysis"""  
    from data_analyzer import ManufacturingKPIAnalyzer
    
    analyzer = ManufacturingKPIAnalyzer(data_path)
    visualizer = ManufacturingVisualizer(analyzer)
    return visualizer.plot_trends(metric=metric)