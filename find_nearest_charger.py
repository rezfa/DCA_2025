# Finds the closest charging station from the current location

def find_nearest_charger(source, Inputs):
    chargers = Inputs.chargers 
    return min(chargers, key=lambda ch: distance(source, ch))