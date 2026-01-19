"""
IT Load Model for Grid-Aware Data Center Optimization

Models flexible IT workload with base and flexible components.
Power consumption is based on server utilization and all IT power becomes heat.
"""

import numpy as np


class ITLoadModel:
    """Models data center IT load with flexible and base workloads."""
    
    def __init__(self, config):
        """
        Initialize IT load model.
        
        Args:
            config: Dictionary with configuration:
                - base_capacity_kw: Base (critical) workload capacity in kW
                - flex_capacity_kw: Flexible workload capacity in kW
                - num_servers: Number of servers
                - server_idle_power_w: Idle power per server in watts
                - server_max_power_w: Max power per server in watts
        """
        self.base_capacity_kw = config.get('base_capacity_kw', 500)
        self.flex_capacity_kw = config.get('flex_capacity_kw', 500)
        self.total_capacity_kw = self.base_capacity_kw + self.flex_capacity_kw
        
        # Server parameters
        self.num_servers = config.get('num_servers', 1000)
        self.server_idle_power_w = config.get('server_idle_power_w', 100)
        self.server_max_power_w = config.get('server_max_power_w', 300)
        
        # State variables
        self.base_workload = 0.7  # Base load utilization (0-1)
        self.flex_workload = 0.3  # Flexible load utilization (0-1)
        self.current_power_kw = 0
        self.current_heat_btu_hr = 0
        
    def set_workload(self, base_util, flex_util):
        """
        Set workload utilization levels.
        
        Args:
            base_util: Base workload utilization (0-1)
            flex_util: Flexible workload utilization (0-1)
        """
        self.base_workload = np.clip(base_util, 0, 1)
        self.flex_workload = np.clip(flex_util, 0, 1)
        
    def compute_power(self):
        """
        Compute IT power consumption based on current workload.
        
        Uses linear power model: Power = Pidle + (Pmax - Pidle) * utilization
        
        Returns:
            Power consumption in kW
        """
        # Average utilization weighted by capacity
        base_weight = self.base_capacity_kw / self.total_capacity_kw
        flex_weight = self.flex_capacity_kw / self.total_capacity_kw
        avg_utilization = (self.base_workload * base_weight + 
                          self.flex_workload * flex_weight)
        
        # Power per server
        power_per_server_w = (self.server_idle_power_w + 
                             (self.server_max_power_w - self.server_idle_power_w) * 
                             avg_utilization)
        
        # Total power
        total_power_w = power_per_server_w * self.num_servers
        total_power_kw = total_power_w / 1000.0
        
        return total_power_kw
    
    def compute_heat(self, power_kw):
        """
        Compute heat generation from IT equipment.
        
        All electrical power consumed by IT equipment is converted to heat.
        
        Args:
            power_kw: IT power consumption in kW
            
        Returns:
            Heat generation in BTU/hr
        """
        # 1 kW = 3412.14 BTU/hr
        return power_kw * 3412.14
    
    def update(self, dt):
        """
        Update IT load state for one time step.
        
        Args:
            dt: Time step in seconds
            
        Returns:
            Current heat generation in BTU/hr
        """
        self.current_power_kw = self.compute_power()
        self.current_heat_btu_hr = self.compute_heat(self.current_power_kw)
        return self.current_heat_btu_hr
    
    def get_state(self):
        """
        Get current IT load state.
        
        Returns:
            Dictionary with current state metrics
        """
        return {
            'base_workload': self.base_workload,
            'flex_workload': self.flex_workload,
            'total_utilization': (self.base_workload * self.base_capacity_kw + 
                                 self.flex_workload * self.flex_capacity_kw) / 
                                self.total_capacity_kw,
            'power_kw': self.current_power_kw,
            'heat_btu_hr': self.current_heat_btu_hr
        }
    
    def get_flexible_capacity(self):
        """
        Get available flexible workload capacity.
        
        Returns:
            Tuple of (current_flex_kw, max_flex_kw)
        """
        current = self.flex_workload * self.flex_capacity_kw
        maximum = self.flex_capacity_kw
        return current, maximum
