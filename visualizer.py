import matplotlib.pyplot as plt
import seaborn as sns
#import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Set professional styling
plt.style.use('default')
sns.set_palette("husl")

class ManufacturingVisualizer:
    """
    Simple Manufacturing Data Visualizer
    Focus on clear, educational code with essential visualizations
    """
    
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
        
        # Simple color scheme - easy to understand and modify
        self.colors = {
            'excellent': '#4CAF50',   # Green - World class (85%+)
            'good': '#8BC34A',        # Light green - Good (75-84%)
            'fair': '#FFC107',        # Yellow - Fair (65-74%) 
            'poor': '#FF5722',        # Red - Poor (<65%)
            'primary': '#2196F3',     # Blue - Default bars/lines
            'secondary': '#FF9800'    # Orange - Secondary elements
        }
    
    def get_performance_color(self, value):
        """
        Simple function to get color based on performance value
        Educational: Shows clear if/elif logic for color mapping
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
        Educational: Shows subplot creation and multiple chart types
        """
        # Get the data we need
        oee_data = self.analyzer.calculate_oee()
        machine_oee = self.analyzer.calculate_oee(group_by='machine_id')
        
        # Create 2x2 subplot layout - core matplotlib concept
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Manufacturing OEE Overview', fontsize=16, fontweight='bold')
        
        # Chart 1: OEE Components (Horizontal Bar Chart)
        components = ['Availability', 'Performance', 'Quality Rate']
        values = [oee_data['availability'], oee_data['performance'], oee_data['quality_rate']]
        colors = [self.get_performance_color(v) for v in values]
        
        bars = ax1.barh(components, values, color=colors, alpha=0.8)
        ax1.set_xlim(0, 100)
        ax1.set_xlabel('Percentage (%)')
        ax1.set_title('OEE Components')
        
        # Add value labels - important for readability
        for bar, value in zip(bars, values):
            ax1.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                    f'{value:.1f}%', va='center', fontweight='bold')
        
        # Chart 2: Overall OEE (Simple gauge-style)
        oee_value = oee_data['oee']
        
        # Create a simple "gauge" using a pie chart - creative matplotlib use
        sizes = [oee_value, 100 - oee_value]
        colors_gauge = [self.get_performance_color(oee_value), 'lightgray']
        
        wedges, texts = ax2.pie(sizes, colors=colors_gauge, startangle=90, counterclock=False)
        
        # Add center text
        ax2.text(0, 0, f'{oee_value:.1f}%\nOEE', ha='center', va='center', 
                fontsize=20, fontweight='bold')
        ax2.set_title('Overall OEE')
        
        # Chart 3: OEE by Machine (Vertical Bar Chart)
        machines = machine_oee.index.tolist()
        machine_values = machine_oee['oee'].values
        machine_colors = [self.get_performance_color(v) for v in machine_values]
        
        bars = ax3.bar(machines, machine_values, color=machine_colors, alpha=0.8)
        ax3.set_ylabel('OEE (%)')
        ax3.set_title('OEE by Machine')
        ax3.set_ylim(0, 100)
        
        # Add benchmark lines - shows target performance
        ax3.axhline(85, color='green', linestyle='--', alpha=0.7, label='World Class (85%)')
        ax3.axhline(75, color='orange', linestyle='--', alpha=0.7, label='Good (75%)')
        ax3.legend(fontsize=8)
        
        # Add value labels on bars
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
        ax4.set_title('Production: Target vs Actual')
        ax4.set_xticks(x)
        ax4.set_xticklabels(machines)
        ax4.legend()
        
        # Adjust layout to prevent overlap
        plt.tight_layout()
        
        # Save if requested
        if save:
            filename = f"oee_overview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = self.output_dir / filename
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"📊 Saved: {filepath}")
        
        plt.show()
        return fig
    
    def plot_trends(self, metric='oee', days=30, save=True):
        """
        Simple trend analysis over time
        Educational: Shows time-series plotting and date handling
        """
        # Prepare time-series data
        df = self.analyzer.df.copy()
        df['date'] = df['timestamp'].dt.date  # Extract just the date
        
        # Group by date and calculate daily averages - pandas groupby concept
        daily_data = df.groupby('date')[metric].mean()
        
        # Limit to recent days if specified
        if days and len(daily_data) > days:
            daily_data = daily_data.tail(days)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot main trend line
        ax.plot(daily_data.index, daily_data.values, 
               marker='o', linewidth=2, markersize=4, color=self.colors['primary'])
        
        # Add trend line using numpy polyfit - shows mathematical concepts
        x_numeric = np.arange(len(daily_data))
        trend_coeffs = np.polyfit(x_numeric, daily_data.values, 1)  # Linear trend
        trend_line = np.poly1d(trend_coeffs)
        
        ax.plot(daily_data.index, trend_line(x_numeric), 
               linestyle='--', color=self.colors['secondary'], alpha=0.8, 
               label=f'Trend (slope: {trend_coeffs[0]:.2f})')
        
        # Formatting
        ax.set_title(f'{metric.upper()} Trend Analysis (Last {len(daily_data)} days)', 
                    fontsize=14, fontweight='bold')
        ax.set_ylabel(f'{metric.upper()} (%)')
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add benchmark line for OEE
        if metric == 'oee':
            ax.axhline(85, color='green', linestyle=':', alpha=0.7, label='World Class Target')
            ax.axhline(75, color='orange', linestyle=':', alpha=0.7, label='Good Target')
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
        Educational: Shows multiple subplots and consistent formatting
        """
        # Get machine data
        machine_data = self.analyzer.get_machine_comparison()
        machines = machine_data.index.tolist()
        
        # Create 2x2 subplot for key metrics
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Machine Performance Comparison', fontsize=16, fontweight='bold')
        
        # Metric 1: OEE
        oee_values = machine_data['oee'].values
        colors_oee = [self.get_performance_color(v) for v in oee_values]
        
        bars1 = ax1.bar(machines, oee_values, color=colors_oee, alpha=0.8)
        ax1.set_title('OEE by Machine')
        ax1.set_ylabel('OEE (%)')
        ax1.set_ylim(0, 100)
        ax1.axhline(85, color='green', linestyle='--', alpha=0.5)
        
        # Add value labels - reusable pattern
        for bar, value in zip(bars1, oee_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Metric 2: Availability
        avail_values = machine_data['availability'].values
        colors_avail = [self.get_performance_color(v) for v in avail_values]
        
        bars2 = ax2.bar(machines, avail_values, color=colors_avail, alpha=0.8)
        ax2.set_title('Availability by Machine')
        ax2.set_ylabel('Availability (%)')
        ax2.set_ylim(0, 100)
        
        for bar, value in zip(bars2, avail_values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Metric 3: Quality Rate
        quality_values = machine_data['quality_rate'].values
        
        bars3 = ax3.bar(machines, quality_values, color=self.colors['excellent'], alpha=0.8)
        ax3.set_title('Quality Rate by Machine')
        ax3.set_ylabel('Quality Rate (%)')
        ax3.set_ylim(90, 100)  # Zoom in on quality range
        ax3.axhline(95, color='red', linestyle='--', alpha=0.7, label='Target (95%)')
        ax3.legend()
        
        for bar, value in zip(bars3, quality_values):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Metric 4: Total Production
        prod_values = machine_data['actual_production'].values
        
        bars4 = ax4.bar(machines, prod_values, color=self.colors['primary'], alpha=0.8)
        ax4.set_title('Total Production by Machine')
        ax4.set_ylabel('Total Units Produced')
        
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
        Educational: Shows how to combine text and charts
        """
        print("📋 Generating Manufacturing Summary Report...")
        
        # Create multiple charts
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
    """Quick OEE overview - one function call"""
    from data_analyzer import ManufacturingKPIAnalyzer
    
    analyzer = ManufacturingKPIAnalyzer(data_path)
    visualizer = ManufacturingVisualizer(analyzer)
    return visualizer.plot_oee_overview()


def quick_trends(data_path='data/sample_data.csv', metric='oee'):
    """Quick trend analysis - one function call"""  
    from data_analyzer import ManufacturingKPIAnalyzer
    
    analyzer = ManufacturingKPIAnalyzer(data_path)
    visualizer = ManufacturingVisualizer(analyzer)
    return visualizer.plot_trends(metric=metric)