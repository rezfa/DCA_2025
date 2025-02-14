# Ensures that the vehicle can reach the charging station after target

def can_reach_charger_after_target(source, target, soc, Inputs):
    nearest_charger = find_nearest_charger(target, Inputs)
    required_battery = (distance(target, nearest_charger)+distance(source, target)) * Inputs.discharge_rate
    return soc >= required_battery