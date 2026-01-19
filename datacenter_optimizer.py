"""
Main Data Center Optimizer

Orchestrates all components and runs the simulation.
"""

import numpy as np
from datetime import datetime, timedelta
import json

from it_load_model import ITLoadModel
from cooling_model import CoolingModel
from grid_monitor import GridSignalMonitor
from simple_controller import SimpleController


class DataCenterOptimizer:
    """Main orchestrator for grid-aware data center optimization."""
    
    def __init__(self, config):
        """
        Initialize the optimizer.
        
        Args:
            config: Dictionary with system configuration
        """
        self.config = config
        
        # Initialize components
        self.it_load = ITLoadModel(config.get('it_load', {}))
        self.cooling = CoolingModel(config.get('cooling', {}))
        self.grid = GridSignalMonitor(config.get('grid', {}))
        self.controller = SimpleController(config.get('controller', {}))
        
        # Simulation parameters
        self.timestep = config.get('timestep_seconds', 300)  # 5 minutes default
        self.current_time = config.get('start_time', datetime.now())
        
        # Metrics history
        self.history = {
            'time': [],
            'it_power_kw': [],
            'cooling_power_kw': [],
            'total_power_kw': [],
            'pue': [],
            'base_workload': [],
            'flex_workload': [],
            'renewable_pct': [],
            'grid_stress': [],
            'price_per_kwh': [],
            'carbon_intensity': [],
            'cooling_mode': [],
            'total_cost': [],
            'total_carbon': []
        }
        
    def get_system_state(self):
        """
        Get current system state from all components.
        
        Returns:
            Dictionary with complete system state
        """
        return {
            'it_load': self.it_load.get_state(),
            'cooling': self.cooling.get_state(),
            'grid': self.grid.current_state,
            'controller': self.controller.get_state(),
            'time': self.current_time
        }
    
    def step(self):
        """
        Execute one simulation time step.
        
        Returns:
            Dictionary with step metrics
        """
        # Update grid conditions (includes outdoor temp for cooling)
        grid_state = self.grid.update(self.timestep)
        
        # Add outdoor temperature to grid state (simulated)
        hour = self.current_time.hour
        # Simple outdoor temp model: cooler at night, warmer during day
        base_temp = 15
        daily_variation = 10 * np.sin((hour - 6) * np.pi / 12)
        outdoor_temp = base_temp + daily_variation
        grid_state['outdoor_temp_c'] = outdoor_temp
        self.cooling.set_outdoor_temp(outdoor_temp)
        
        # Get current system state
        system_state = self.get_system_state()
        
        # Compute optimal control actions
        control = self.controller.compute_control(system_state, grid_state)
        
        # Apply control to IT load
        self.it_load.set_workload(
            control['workload_base'],
            control['workload_flex']
        )
        
        # Apply control to cooling
        self.cooling.set_supply_temp(control['cooling_params']['supply_temp'])
        
        # Update IT load (generates heat)
        heat_load = self.it_load.update(self.timestep)
        
        # Update cooling (consumes power to remove heat)
        cooling_power = self.cooling.update(self.timestep, heat_load)
        
        # Compute PUE
        it_power = self.it_load.current_power_kw
        pue = self.cooling.compute_current_pue(it_power)
        
        # Compute costs and carbon
        total_power = it_power + cooling_power
        energy_kwh = total_power * (self.timestep / 3600.0)  # Convert to kWh
        cost = energy_kwh * grid_state['price_per_kwh']
        carbon = energy_kwh * grid_state['carbon_intensity_gco2_kwh']
        
        # Record metrics
        self.history['time'].append(self.current_time)
        self.history['it_power_kw'].append(it_power)
        self.history['cooling_power_kw'].append(cooling_power)
        self.history['total_power_kw'].append(total_power)
        self.history['pue'].append(pue)
        self.history['base_workload'].append(self.it_load.base_workload)
        self.history['flex_workload'].append(self.it_load.flex_workload)
        self.history['renewable_pct'].append(grid_state['renewable_pct'])
        self.history['grid_stress'].append(grid_state['grid_stress'])
        self.history['price_per_kwh'].append(grid_state['price_per_kwh'])
        self.history['carbon_intensity'].append(grid_state['carbon_intensity_gco2_kwh'])
        self.history['cooling_mode'].append(self.cooling.current_mode)
        self.history['total_cost'].append(cost)
        self.history['total_carbon'].append(carbon)
        
        # Advance time
        self.current_time += timedelta(seconds=self.timestep)
        
        return {
            'time': self.current_time,
            'it_power_kw': it_power,
            'cooling_power_kw': cooling_power,
            'total_power_kw': total_power,
            'pue': pue,
            'cost': cost,
            'carbon_g': carbon
        }
    
    def run(self, duration_hours=24):
        """
        Run simulation for specified duration.
        
        Args:
            duration_hours: Simulation duration in hours
            
        Returns:
            Dictionary with complete results
        """
        num_steps = int((duration_hours * 3600) / self.timestep)
        
        print(f"Starting simulation for {duration_hours} hours ({num_steps} steps)")
        print(f"Time step: {self.timestep} seconds ({self.timestep/60:.1f} minutes)")
        print("-" * 60)
        
        for i in range(num_steps):
            metrics = self.step()
            
            # Print progress every hour
            if i % (3600 // self.timestep) == 0:
                hour = i * self.timestep / 3600
                print(f"Hour {hour:5.1f} | "
                      f"Power: {metrics['total_power_kw']:6.1f} kW | "
                      f"PUE: {metrics['pue']:4.2f} | "
                      f"Renewable: {self.grid.current_state['renewable_pct']*100:5.1f}% | "
                      f"Flex Load: {self.it_load.flex_workload*100:5.1f}%")
        
        print("-" * 60)
        print("Simulation complete!")
        
        return self.get_results()
    
    def get_results(self):
        """
        Get simulation results and summary statistics.
        
        Returns:
            Dictionary with results and statistics
        """
        # Compute summary statistics
        total_energy_kwh = sum(self.history['total_power_kw']) * (self.timestep / 3600.0)
        total_cost = sum(self.history['total_cost'])
        total_carbon_kg = sum(self.history['total_carbon']) / 1000.0
        avg_pue = np.mean(self.history['pue'])
        min_pue = np.min(self.history['pue'])
        max_pue = np.max(self.history['pue'])
        
        summary = {
            'total_energy_kwh': total_energy_kwh,
            'total_cost_usd': total_cost,
            'total_carbon_kg': total_carbon_kg,
            'avg_pue': avg_pue,
            'min_pue': min_pue,
            'max_pue': max_pue,
            'avg_renewable_pct': np.mean(self.history['renewable_pct']),
            'avg_flex_workload': np.mean(self.history['flex_workload'])
        }
        
        return {
            'history': self.history,
            'summary': summary,
            'config': self.config
        }
    
    def save_results(self, filename='results.json'):
        """Save results to JSON file."""
        results = self.get_results()
        
        # Convert datetime objects to strings
        results['history']['time'] = [t.isoformat() for t in results['history']['time']]
        if isinstance(results['config'].get('start_time'), datetime):
            results['config']['start_time'] = results['config']['start_time'].isoformat()
        if 'grid' in results['config'] and isinstance(results['config']['grid'].get('start_time'), datetime):
            results['config']['grid']['start_time'] = results['config']['grid']['start_time'].isoformat()
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {filename}")


def create_default_config():
    """Create default configuration."""
    return {
        'it_load': {
            'base_capacity_kw': 500,
            'flex_capacity_kw': 500,
            'num_servers': 1000,
            'server_idle_power_w': 100,
            'server_max_power_w': 300
        },
        'cooling': {
            'supply_temp_c': 18,
            'outdoor_temp_c': 20,
            'chiller_cop': 3.5,
            'free_cooling_threshold_c': 15,
            'thermal_mass_btu_f': 50000,
            'target_temp_c': 22
        },
        'grid': {
            'base_price_per_kwh': 0.12,
            'price_multiplier_peak': 2.0,
            'start_time': datetime.now()
        },
        'controller': {
            'workload_adjustment_rate': 0.2,
            'renewable_threshold_high': 0.6,
            'renewable_threshold_low': 0.3,
            'stress_threshold_high': 0.7
        },
        'timestep_seconds': 300,  # 5 minutes
        'start_time': datetime.now()
    }


if __name__ == '__main__':
    # Create and run simulation
    config = create_default_config()
    optimizer = DataCenterOptimizer(config)
    
    # Run 24-hour simulation
    results = optimizer.run(duration_hours=24)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SIMULATION SUMMARY")
    print("=" * 60)
    summary = results['summary']
    print(f"Total Energy:     {summary['total_energy_kwh']:10.2f} kWh")
    print(f"Total Cost:       ${summary['total_cost_usd']:10.2f}")
    print(f"Total Carbon:     {summary['total_carbon_kg']:10.2f} kg CO2")
    print(f"Average PUE:      {summary['avg_pue']:10.3f}")
    print(f"PUE Range:        {summary['min_pue']:.3f} - {summary['max_pue']:.3f}")
    print(f"Avg Renewable:    {summary['avg_renewable_pct']*100:10.1f}%")
    print(f"Avg Flex Load:    {summary['avg_flex_workload']*100:10.1f}%")
    print("=" * 60)
    
    # Save results
    optimizer.save_results('results.json')
