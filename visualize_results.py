"""
Visualization Script for Data Center Optimization Results

Generates plots showing system behavior over the simulation period.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def load_results(filename='results.json'):
    """Load results from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)

def plot_results(results, save_plots=True):
    """
    Create comprehensive visualizations of simulation results.
    
    Args:
        results: Results dictionary from simulation
        save_plots: If True, save plots to files
    """
    history = results['history']
    summary = results['summary']
    
    # Convert time to hours for plotting
    num_steps = len(history['pue'])
    hours = np.arange(num_steps) * (5/60)  # 5-minute timesteps
    
    # Create figure with 6 subplots - use constrained_layout to prevent overlap
    fig = plt.figure(figsize=(16, 14), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.25)
    
    # Add title with proper spacing
    fig.suptitle('Grid-Aware Data Center Optimization - 24 Hour Simulation', 
                 fontsize=15, fontweight='bold', y=0.995)
    
    # 1. Power Consumption
    ax = fig.add_subplot(gs[0, 0])
    ax.plot(hours, history['it_power_kw'], label='IT Power', linewidth=2)
    ax.plot(hours, history['cooling_power_kw'], label='Cooling Power', linewidth=2)
    ax.plot(hours, history['total_power_kw'], label='Total Power', 
            linewidth=2, linestyle='--', color='black')
    ax.set_xlabel('Hour of Day', fontsize=10)
    ax.set_ylabel('Power (kW)', fontsize=10)
    ax.set_title('Power Consumption Over Time', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    
    # 2. PUE Dynamics
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(hours, history['pue'], linewidth=2, color='darkred')
    ax.axhline(y=summary['avg_pue'], color='gray', linestyle='--', 
               label=f'Avg PUE: {summary["avg_pue"]:.3f}')
    ax.set_xlabel('Hour of Day', fontsize=10)
    ax.set_ylabel('PUE', fontsize=10)
    ax.set_title('Power Usage Effectiveness (PUE)', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([1.0, max(history['pue']) * 1.1])
    
    # 3. Workload Distribution
    ax = fig.add_subplot(gs[1, 0])
    ax.fill_between(hours, 0, np.array(history['base_workload']) * 100, 
                     label='Base Workload', alpha=0.7, color='steelblue')
    ax.fill_between(hours, np.array(history['base_workload']) * 100,
                     (np.array(history['base_workload']) + 
                      np.array(history['flex_workload'])) * 100,
                     label='Flexible Workload', alpha=0.7, color='orange')
    ax.set_xlabel('Hour of Day', fontsize=10)
    ax.set_ylabel('Utilization (%)', fontsize=10)
    ax.set_title('IT Workload Distribution', fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 200])
    
    # 4. Grid Conditions
    ax = fig.add_subplot(gs[1, 1])
    ax2 = ax.twinx()
    
    l1 = ax.plot(hours, np.array(history['renewable_pct']) * 100, 
                 label='Renewable %', linewidth=2, color='green')
    l2 = ax2.plot(hours, np.array(history['grid_stress']) * 100, 
                  label='Grid Stress', linewidth=2, color='red', linestyle='--')
    
    ax.set_xlabel('Hour of Day', fontsize=10)
    ax.set_ylabel('Renewable Energy (%)', color='green', fontsize=10)
    ax2.set_ylabel('Grid Stress (%)', color='red', fontsize=10)
    ax.set_title('Grid Conditions', fontsize=11)
    ax.tick_params(axis='y', labelcolor='green')
    ax2.tick_params(axis='y', labelcolor='red')
    ax.grid(True, alpha=0.3)
    
    # Combined legend
    lns = l1 + l2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc='upper left', fontsize=9)
    
    # 5. Cost and Carbon
    ax = fig.add_subplot(gs[2, 0])
    cumulative_cost = np.cumsum(history['total_cost'])
    cumulative_carbon = np.cumsum(history['total_carbon']) / 1000  # Convert to kg
    
    ax2 = ax.twinx()
    l1 = ax.plot(hours, cumulative_cost, label='Cumulative Cost', 
                 linewidth=2, color='darkblue')
    l2 = ax2.plot(hours, cumulative_carbon, label='Cumulative Carbon', 
                  linewidth=2, color='brown', linestyle='--')
    
    ax.set_xlabel('Hour of Day', fontsize=10)
    ax.set_ylabel('Cost ($)', color='darkblue', fontsize=10)
    ax2.set_ylabel('Carbon (kg CO2)', color='brown', fontsize=10)
    ax.set_title('Cumulative Cost and Carbon Emissions', fontsize=11)
    ax.tick_params(axis='y', labelcolor='darkblue')
    ax2.tick_params(axis='y', labelcolor='brown')
    ax.grid(True, alpha=0.3)
    
    lns = l1 + l2
    labs = [l.get_label() for l in lns]
    ax.legend(lns, labs, loc='upper left', fontsize=9)
    
    # 6. Electricity Price
    ax = fig.add_subplot(gs[2, 1])
    ax.plot(hours, history['price_per_kwh'], linewidth=2, color='purple')
    ax.fill_between(hours, 0, history['price_per_kwh'], alpha=0.3, color='purple')
    ax.set_xlabel('Hour of Day', fontsize=10)
    ax.set_ylabel('Price ($/kWh)', fontsize=10)
    ax.set_title('Electricity Price', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # constrained_layout handles spacing automatically, no need for tight_layout
    
    if save_plots:
        plt.savefig('simulation_results.png', dpi=300, bbox_inches='tight')
        print("Plot saved to simulation_results.png")
    
    plt.show()
    
    return fig

def print_summary(results):
    """Print formatted summary of results."""
    summary = results['summary']
    
    print("\n" + "=" * 70)
    print("DETAILED SIMULATION SUMMARY")
    print("=" * 70)
    
    print(f"\n[Energy Metrics]:")
    print(f"   Total Energy Consumed:      {summary['total_energy_kwh']:>10.2f} kWh")
    print(f"   Average Power:              {summary['total_energy_kwh']/24:>10.2f} kW")
    
    print(f"\n[Economic Metrics]:")
    print(f"   Total Cost:                 ${summary['total_cost_usd']:>10.2f}")
    print(f"   Average Cost per kWh:       ${summary['total_cost_usd']/summary['total_energy_kwh']:>10.3f}")
    
    print(f"\n[Environmental Metrics]:")
    print(f"   Total Carbon Emissions:     {summary['total_carbon_kg']:>10.2f} kg CO2")
    print(f"   Carbon Intensity:           {summary['total_carbon_kg']/summary['total_energy_kwh']*1000:>10.1f} gCO2/kWh")
    
    print(f"\n[Efficiency Metrics]:")
    print(f"   Average PUE:                {summary['avg_pue']:>10.3f}")
    print(f"   Best PUE:                   {summary['min_pue']:>10.3f}")
    print(f"   Worst PUE:                  {summary['max_pue']:>10.3f}")
    print(f"   PUE Improvement Potential:  {((summary['max_pue']-summary['min_pue'])/summary['max_pue']*100):>10.1f}%")
    
    print(f"\n[Grid Integration Metrics]:")
    print(f"   Avg Renewable Utilization:  {summary['avg_renewable_pct']*100:>10.1f}%")
    print(f"   Avg Flexible Workload:      {summary['avg_flex_workload']*100:>10.1f}%")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    # Load and visualize results
    print("Loading simulation results...")
    results = load_results('results.json')
    
    # Print summary
    print_summary(results)
    
    # Create plots
    print("\nGenerating visualizations...")
    plot_results(results, save_plots=True)
    
    print("\n[DONE] Visualization complete!")
