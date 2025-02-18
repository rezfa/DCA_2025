from load_data import load_instance, Vehicles
from initial_solution import initial_solution
from evaluate_solution import determine_unloading_completion_time

inputs_data = "Toys/Not Annotated/943.inst"

inputs = load_instance(inputs_data)

vehicles = {i+1: Vehicles(vehicle_id=veh[0], initial_battery=veh[1]) for i, veh in enumerate(inputs.vehicles)}

vehicles = initial_solution(inputs, vehicles)

for vehicle in list(vehicles.keys()):
    vehicles[vehicle].unloading_completion_time = determine_unloading_completion_time(vehicles[vehicle],inputs)