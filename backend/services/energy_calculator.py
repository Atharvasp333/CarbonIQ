def calculate_energy(runtime_hours: float, cpu_utilization: float) -> float:
    """
    Estimates energy consumption based on runtime and CPU utilization.
    Assume a base server capacity of 100 watts (0.1 kW).
    Adjust power based on CPU utilization:
    50% CPU -> 0.05 kW
    80% CPU -> 0.08 kW
    
    Formula:
    Power (kW) = 0.1 * (cpu_utilization / 100.0)
    Energy (kWh) = Power (kW) * runtime_hours
    """
    # Assuming max power is 0.1 kW (100W), and it scales linearly with CPU utilization
    power_kw = 0.1 * (cpu_utilization / 100.0)
    
    # Calculate energy
    energy_kwh = power_kw * runtime_hours
    return energy_kwh
