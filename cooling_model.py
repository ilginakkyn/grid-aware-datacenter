"""
Cooling Infrastructure Model for Grid-Aware Data Center Optimization

Models cooling system with dynamic PUE calculation, multiple cooling modes,
and thermal dynamics.
"""

import numpy as np


class CoolingModel:
    """Models data center cooling infrastructure with dynamic PUE."""
    
    # Cooling modes
    MODE_FREE = 'free_cooling'
    MODE_HYBRID = 'hybrid'
    MODE_MECHANICAL = 'mechanical'
    
    def __init__(self, config):
        """
        Initialize cooling model.
        
        Args:
            config: Dictionary with configuration:
                - supply_temp_c: Supply air temperature setpoint in Celsius
                - outdoor_temp_c: Outdoor temperature in Celsius
                - chiller_cop: Chiller coefficient of performance
                - free_cooling_threshold_c: Max outdoor temp for free cooling
                - thermal_mass_btu_f: Thermal mass in BTU/°F
                - target_temp_c: Target data center temperature
        """
        self.supply_temp_setpoint = config.get('supply_temp_c', 18)
        self.outdoor_temp = config.get('outdoor_temp_c', 20)
        self.chiller_cop = config.get('chiller_cop', 3.5)
        self.free_cooling_threshold = config.get('free_cooling_threshold_c', 15)
        
        # Thermal dynamics
        self.thermal_mass = config.get('thermal_mass_btu_f', 50000)
        self.target_temp = config.get('target_temp_c', 22)
        self.current_temp = self.target_temp
        
        # State variables
        self.current_mode = self.MODE_HYBRID
        self.current_cooling_power_kw = 0
        self.current_pue = 1.2
        
        # Fan and pump overhead (as fraction of cooling load)
        self.fan_pump_overhead = config.get('fan_pump_overhead', 0.10)
        
    def set_outdoor_temp(self, temp_c):
        """Set outdoor temperature."""
        self.outdoor_temp = temp_c
        
    def set_supply_temp(self, temp_c):
        """Set supply air temperature setpoint."""
        self.supply_temp_setpoint = temp_c
        
    def compute_free_cooling_ratio(self):
        """
        Compute the fraction of cooling that can be done via free cooling.
        
        Returns:
            Ratio between 0 (no free cooling) and 1 (full free cooling)
        """
        if self.outdoor_temp <= self.free_cooling_threshold:
            return 1.0
        elif self.outdoor_temp >= self.target_temp:
            return 0.0
        else:
            # Linear interpolation
            return 1.0 - ((self.outdoor_temp - self.free_cooling_threshold) / 
                         (self.target_temp - self.free_cooling_threshold))
    
    def determine_cooling_mode(self):
        """
        Determine optimal cooling mode based on outdoor conditions.
        
        Returns:
            Cooling mode string
        """
        free_ratio = self.compute_free_cooling_ratio()
        
        if free_ratio >= 0.95:
            return self.MODE_FREE
        elif free_ratio > 0.1:
            return self.MODE_HYBRID
        else:
            return self.MODE_MECHANICAL
    
    def compute_cooling_power(self, heat_load_btu_hr, mode=None):
        """
        Compute cooling power consumption based on heat load and mode.
        
        Args:
            heat_load_btu_hr: Heat load to remove in BTU/hr
            mode: Cooling mode (defaults to auto-select)
            
        Returns:
            Cooling power consumption in kW
        """
        if mode is None:
            mode = self.determine_cooling_mode()
        
        # Convert heat load to kW
        heat_load_kw = heat_load_btu_hr / 3412.14
        
        if mode == self.MODE_FREE:
            # Free cooling: only fans and pumps
            # Overhead is typically 2-5% of heat load
            cooling_power_kw = heat_load_kw * 0.03
            
        elif mode == self.MODE_HYBRID:
            # Partial economizer
            free_ratio = self.compute_free_cooling_ratio()
            
            # Mechanical cooling for portion not covered by free cooling
            mech_load_kw = heat_load_kw * (1 - free_ratio)
            mech_power_kw = mech_load_kw / self.chiller_cop
            
            # Fan/pump power for entire load
            fan_pump_power_kw = heat_load_kw * self.fan_pump_overhead
            
            cooling_power_kw = mech_power_kw + fan_pump_power_kw
            
        else:  # MODE_MECHANICAL
            # Full mechanical cooling
            # Chiller power
            chiller_power_kw = heat_load_kw / self.chiller_cop
            
            # Fan and pump power
            fan_pump_power_kw = heat_load_kw * self.fan_pump_overhead
            
            cooling_power_kw = chiller_power_kw + fan_pump_power_kw
        
        return cooling_power_kw
    
    def compute_pue(self, it_power_kw, cooling_power_kw):
        """
        Compute Power Usage Effectiveness.
        
        PUE = Total Facility Power / IT Equipment Power
            = (IT Power + Cooling Power + Other) / IT Power
        
        For simplicity, we only consider cooling overhead.
        
        Args:
            it_power_kw: IT equipment power in kW
            cooling_power_kw: Cooling system power in kW
            
        Returns:
            PUE value (typically 1.0 to 2.5)
        """
        if it_power_kw <= 0:
            return 1.0
        
        # Add small overhead for lighting, UPS losses, etc. (5%)
        other_overhead_kw = it_power_kw * 0.05
        
        total_power_kw = it_power_kw + cooling_power_kw + other_overhead_kw
        pue = total_power_kw / it_power_kw
        
        return pue
    
    def update_thermal_state(self, heat_load_btu_hr, dt):
        """
        Update data center temperature based on heat load and cooling.
        
        Simple thermal model: dT/dt = (Q_in - Q_out) / C
        
        Args:
            heat_load_btu_hr: Heat generation in BTU/hr
            dt: Time step in seconds
        """
        # Heat accumulation
        heat_in_btu = heat_load_btu_hr * (dt / 3600.0)  # Convert hr to sec
        
        # Cooling removes heat to maintain setpoint
        # Simplified: assume cooling perfectly matches load
        temp_rise = (heat_in_btu / self.thermal_mass) if self.thermal_mass > 0 else 0
        
        # Temperature dynamics with cooling feedback
        self.current_temp = self.target_temp + temp_rise * 0.1  # Damped response
        
    def update(self, dt, heat_load_btu_hr):
        """
        Update cooling system state for one time step.
        
        Args:
            dt: Time step in seconds
            heat_load_btu_hr: IT heat load in BTU/hr
            
        Returns:
            Tuple of (cooling_power_kw, pue)
        """
        # Determine optimal cooling mode
        self.current_mode = self.determine_cooling_mode()
        
        # Compute cooling power
        self.current_cooling_power_kw = self.compute_cooling_power(
            heat_load_btu_hr, 
            self.current_mode
        )
        
        # Update thermal state
        self.update_thermal_state(heat_load_btu_hr, dt)
        
        return self.current_cooling_power_kw
    
    def compute_current_pue(self, it_power_kw):
        """
        Compute current PUE based on latest cooling power.
        
        Args:
            it_power_kw: IT power in kW
            
        Returns:
            Current PUE value
        """
        self.current_pue = self.compute_pue(it_power_kw, self.current_cooling_power_kw)
        return self.current_pue
    
    def get_state(self):
        """
        Get current cooling system state.
        
        Returns:
            Dictionary with current state metrics
        """
        return {
            'mode': self.current_mode,
            'cooling_power_kw': self.current_cooling_power_kw,
            'pue': self.current_pue,
            'current_temp_c': self.current_temp,
            'outdoor_temp_c': self.outdoor_temp,
            'supply_temp_c': self.supply_temp_setpoint,
            'free_cooling_ratio': self.compute_free_cooling_ratio()
        }
