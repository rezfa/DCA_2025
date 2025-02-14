# Checks if the vehicle can reach the target with current state of charge (SOC)

def can_reach_target(source, target, soc, Inputs):
    return soc >= distance(source, target) * Inputs.discharge_rate