"""
Simple Heuristic Controller for Grid-Aware Data Center Optimization

Uses rule-based control to adjust workload and cooling based on grid conditions.
This is a simplified alternative to full MPC for faster execution.
"""

import numpy as np


class SimpleController:
    """Simple heuristic controller for data center optimization."""
    
    def __init__(self, config):
        """
        Initialize controller.
        
        Args:
            config: Dictionary with configuration:
                - workload_adjustment_rate: How aggressively to adjust workload (0-1)
                - renewable_threshold_high: Renewable % to increase workload
                - renewable_threshold_low: Renewable % to decrease workload
                - stress_threshold_high: Stress level to reduce workload
        """
        self.adjustment_rate = config.get('workload_adjustment_rate', 0.2)
        self.renewable_threshold_high = config.get('renewable_threshold_high', 0.6)
        self.renewable_threshold_low = config.get('renewable_threshold_low', 0.3)
        self.stress_threshold_high = config.get('stress_threshold_high', 0.7)
        
        # Control state
        self.target_base_util = 0.7
        self.target_flex_util = 0.3
        
    def compute_control(self, system_state, grid_state):
        """
        Compute control actions based on system and grid state.
        
        Control logic:
        1. High renewables + low stress → increase flexible workload
        2. Low renewables + high stress → decrease flexible workload
        3. Keep base workload stable (critical services)
        4. Adjust cooling based on outdoor temp
        
        Args:
            system_state: Current data center state
            grid_state: Current grid conditions
            
        Returns:
            Dictionary with control actions
        """
        renewable_pct = grid_state['renewable_pct']
        stress_level = grid_state['grid_stress']
        outdoor_temp = grid_state.get('outdoor_temp_c', 20)
        
        # Base workload remains stable (critical services)
        base_target = 0.7
        
        # Flexible workload adjusts based on grid
        current_flex = system_state['it_load']['flex_workload']
        
        if renewable_pct >= self.renewable_threshold_high and stress_level < 0.5:
            # Good conditions: increase flexible load
            flex_target = min(1.0, current_flex + self.adjustment_rate)
        elif renewable_pct <= self.renewable_threshold_low or stress_level >= self.stress_threshold_high:
            # Poor conditions: decrease flexible load
            flex_target = max(0.1, current_flex - self.adjustment_rate)
        else:
            # Moderate conditions: maintain current level
            flex_target = current_flex
        
        # Cooling parameters
        # Use free cooling when possible
        if outdoor_temp < 15:
            cooling_mode = 'free_cooling'
            supply_temp = 20  # Can be warmer with free cooling
        elif outdoor_temp < 25:
            cooling_mode = 'hybrid'
            supply_temp = 18
        else:
            cooling_mode = 'mechanical'
            supply_temp = 16  # Need cooler air in hot conditions
        
        # Store targets
        self.target_base_util = base_target
        self.target_flex_util = flex_target
        
        return {
            'workload_base': base_target,
            'workload_flex': flex_target,
            'cooling_params': {
                'supply_temp': supply_temp,
                'mode': cooling_mode
            }
        }
    
    def get_state(self):
        """Get current controller state."""
        return {
            'target_base_util': self.target_base_util,
            'target_flex_util': self.target_flex_util
        }
