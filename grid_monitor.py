"""
Grid Signal Monitor for Grid-Aware Data Center Optimization

Monitors and simulates grid conditions including renewable availability,
grid stress levels, dynamic pricing, and carbon intensity.
"""

import numpy as np
from datetime import datetime, timedelta


class GridSignalMonitor:
    """Monitors grid conditions and generates control signals."""
    
    def __init__(self, config):
        """
        Initialize grid monitor.
        
        Args:
            config: Dictionary with configuration:
                - base_price_per_kwh: Base electricity price in $/kWh
                - start_time: Simulation start time (datetime)
                - renewable_profile: Optional 24-hour renewable profile
                - price_multiplier_peak: Price multiplier during peak hours
        """
        self.base_price = config.get('base_price_per_kwh', 0.12)
        self.price_multiplier_peak = config.get('price_multiplier_peak', 2.0)
        self.start_time = config.get('start_time', datetime.now())
        
        # Generate realistic profiles
        self.renewable_profile = self._generate_renewable_profile()
        self.price_profile = self._generate_price_profile()
        self.carbon_profile = self._generate_carbon_profile()
        
        # Current state
        self.current_time = self.start_time
        self.current_state = {}
        
    def _generate_renewable_profile(self):
        """
        Generate 24-hour renewable energy availability profile.
        
        Simulates solar + wind mix with peak solar during midday.
        
        Returns:
            Array of 24 hourly values (0-1 representing 0-100%)
        """
        hours = np.arange(24)
        
        # Solar component (peaks at noon)
        solar = np.maximum(0, np.sin((hours - 6) * np.pi / 12))
        
        # Wind component (variable, slightly higher at night)
        wind_base = 0.4
        wind_variation = 0.2 * np.sin(hours * np.pi / 12 + np.pi)
        wind = wind_base + wind_variation
        
        # Combined (weighted average: 60% solar, 40% wind)
        renewable = 0.6 * solar + 0.4 * wind
        
        # Normalize to 0-1 range
        renewable = np.clip(renewable, 0, 1)
        
        return renewable
    
    def _generate_price_profile(self):
        """
        Generate 24-hour electricity price profile.
        
        Higher prices during peak hours (afternoon/evening).
        
        Returns:
            Array of 24 hourly price values in $/kWh
        """
        hours = np.arange(24)
        
        # Peak hours: 4 PM to 9 PM (16-21)
        price = np.ones(24) * self.base_price
        
        for h in range(24):
            if 16 <= h < 21:  # Peak hours
                price[h] = self.base_price * self.price_multiplier_peak
            elif 12 <= h < 16 or 21 <= h < 23:  # Shoulder hours
                price[h] = self.base_price * 1.3
            # else: off-peak (base price)
        
        return price
    
    def _generate_carbon_profile(self):
        """
        Generate 24-hour carbon intensity profile.
        
        Lower when renewable availability is high.
        
        Returns:
            Array of 24 hourly carbon intensity values in gCO2/kWh
        """
        # Inverse of renewable availability
        # High renewables = low carbon
        base_carbon = 500  # gCO2/kWh for fossil fuel grid
        clean_carbon = 50   # gCO2/kWh for renewable grid
        
        carbon = base_carbon - (base_carbon - clean_carbon) * self.renewable_profile
        
        return carbon
    
    def get_hour_of_day(self, timestamp=None):
        """Get hour of day from timestamp."""
        if timestamp is None:
            timestamp = self.current_time
        return timestamp.hour
    
    def compute_stress_level(self, hour):
        """
        Compute grid stress level for given hour.
        
        Stress is high during peak demand hours and low renewable availability.
        
        Args:
            hour: Hour of day (0-23)
            
        Returns:
            Stress level (0-1)
        """
        # Base stress from demand pattern
        if 16 <= hour < 21:  # Peak hours
            demand_stress = 0.7
        elif 12 <= hour < 16 or 21 <= hour < 23:  # Shoulder
            demand_stress = 0.4
        else:  # Off-peak
            demand_stress = 0.2
        
        # Renewable availability reduces stress
        renewable_factor = 1.0 - self.renewable_profile[hour]
        
        # Combined stress
        stress = demand_stress * (0.5 + 0.5 * renewable_factor)
        
        # Add small random variation
        stress += np.random.uniform(-0.1, 0.1)
        stress = np.clip(stress, 0, 1)
        
        return stress
    
    def get_current_state(self, timestamp=None):
        """
        Get current grid state.
        
        Args:
            timestamp: Current time (defaults to internal time)
            
        Returns:
            Dictionary with grid state metrics
        """
        if timestamp is not None:
            self.current_time = timestamp
        
        hour = self.get_hour_of_day()
        
        self.current_state = {
            'timestamp': self.current_time,
            'hour': hour,
            'renewable_pct': float(self.renewable_profile[hour]),
            'grid_stress': float(self.compute_stress_level(hour)),
            'price_per_kwh': float(self.price_profile[hour]),
            'carbon_intensity_gco2_kwh': float(self.carbon_profile[hour])
        }
        
        return self.current_state
    
    def update(self, dt):
        """
        Update grid monitor for one time step.
        
        Args:
            dt: Time step in seconds
        """
        self.current_time += timedelta(seconds=dt)
        return self.get_current_state()
    
    def get_renewable_forecast(self, hours_ahead=4):
        """
        Get renewable availability forecast.
        
        Args:
            hours_ahead: Number of hours to forecast
            
        Returns:
            Array of forecasted renewable percentages
        """
        current_hour = self.get_hour_of_day()
        forecast = []
        
        for i in range(hours_ahead):
            future_hour = (current_hour + i) % 24
            forecast.append(self.renewable_profile[future_hour])
        
        return np.array(forecast)
