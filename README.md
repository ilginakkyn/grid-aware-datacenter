# Grid-Aware Data Center Optimization System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simulation system that models a data center as a coupled IT load and cooling infrastructure, optimizing total power consumption by dynamically adjusting PUE based on grid conditions and flexible workload management.

## 🎯 Features

- **Flexible IT Workload Management**: Separates base (critical) and flexible (deferrable) workloads
- **Dynamic PUE Optimization**: Adjusts cooling efficiency (1.08-1.44) based on workload and outdoor conditions
- **Grid-Aware Control**: Responds to renewable availability (0-100%), grid stress, and electricity pricing
- **Multiple Cooling Modes**: Free cooling, hybrid, and mechanical cooling with automatic mode selection
- **Comprehensive Metrics**: Tracks power, cost, carbon emissions, and efficiency in real-time

## 📊 Simulation Results

24-hour simulation demonstrates:
- **PUE Range**: 1.08 (best with free cooling) to 1.44 (peak load with mechanical cooling)
- **Grid Responsiveness**: Workload increases to 100% during high renewable periods (64-76%)
- **Cost Optimization**: Reduces load during peak pricing hours
- **Carbon Awareness**: Higher utilization during low-carbon grid conditions

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ilginakkyn/grid-aware-datacenter.git
cd grid-aware-datacenter

# Install dependencies
pip install -r requirements.txt
```

### Running the Simulation

```bash
# Run 24-hour simulation
python datacenter_optimizer.py

# Visualize results
python visualize_results.py
```

## 📁 Project Structure

```
├── datacenter_optimizer.py   # Main simulation orchestrator
├── it_load_model.py          # IT workload management
├── cooling_model.py          # Cooling system with PUE calculation
├── grid_monitor.py           # Grid signal simulation
├── simple_controller.py      # Optimization controller
├── visualize_results.py      # Result visualization
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔧 Configuration

Customize simulation parameters in `datacenter_optimizer.py`:

```python
config = {
    'it_load': {
        'base_capacity_kw': 500,      # Base workload capacity
        'flex_capacity_kw': 500,      # Flexible workload capacity
        'num_servers': 1000,          # Number of servers
    },
    'cooling': {
        'chiller_cop': 3.5,           # Cooling efficiency
        'free_cooling_threshold_c': 15,
    },
    'controller': {
        'renewable_threshold_high': 0.6,   # Increase load threshold
        'stress_threshold_high': 0.7,      # Reduce load threshold
    },
}
```

## 📈 Understanding Results

### Key Metrics

- **PUE (Power Usage Effectiveness)**: Total facility power / IT power (lower is better, ideal = 1.0)
- **Total Energy**: Cumulative IT + cooling power consumption
- **Total Cost**: Energy cost based on dynamic electricity pricing
- **Total Carbon**: CO2 emissions based on grid carbon intensity
- **Flexible Workload**: Percentage of deferrable workload being utilized

### Control Behavior

The system automatically:
1. **Increases flexible workload** when renewable availability is high (>60%) and grid stress is low
2. **Decreases flexible workload** during grid stress events or low renewable periods
3. **Switches cooling modes** based on outdoor temperature for optimal efficiency
4. **Maintains base workload** at stable levels for critical services

## 🛠️ System Components

### IT Load Model
Models server power consumption with separate base and flexible workloads. Uses linear power model based on CPU utilization.

### Cooling Model
Implements three cooling modes:
- **Free Cooling**: Uses outdoor air when temperature permits (PUE ~1.08)
- **Hybrid**: Combines free cooling with mechanical cooling (PUE ~1.26-1.35)
- **Mechanical**: Full chiller operation for hot conditions (PUE ~1.44)

### Grid Monitor
Simulates realistic 24-hour profiles for:
- Renewable energy (60% solar + 40% wind)
- Electricity pricing (peak/off-peak)
- Carbon intensity (inversely related to renewables)
- Grid stress levels

### Controller
Heuristic optimization that adjusts workload based on:
- Renewable energy availability
- Grid stress levels
- Outdoor temperature for cooling mode selection

## 📊 Visualization

The `visualize_results.py` script generates comprehensive plots showing:
1. Power consumption over time (IT, cooling, total)
2. PUE dynamics throughout the day
3. Workload distribution (base vs flexible)
4. Grid conditions (renewable % and stress level)
5. Cumulative cost and carbon emissions
6. Electricity pricing profile

## 🔮 Future Enhancements

- **Advanced MPC Controller**: Model Predictive Control using CVXPY for optimal scheduling
- **Real Grid API Integration**: Connect to WattTime or similar for actual carbon signals
- **Multi-Zone Thermal Model**: More accurate temperature distribution modeling
- **Battery Storage**: Energy storage for enhanced load shifting capabilities
- **Web Dashboard**: Real-time monitoring with Flask + SocketIO
- **Demand Response Integration**: Utility DR program participation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**ilginakkyn**  
GitHub: [@ilginakkyn](https://github.com/ilginakkyn)

## 🙏 Acknowledgments

- Research on grid-aware computing and data center optimization
- Model Predictive Control techniques for cooling systems
- Demand response strategies for flexible workloads

---

⭐ If you find this project useful, please consider giving it a star!
