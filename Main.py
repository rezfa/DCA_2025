from load_data import load_instance, Vehicles
from initial_solution import initial_solution
from construct_initial_solution import Init_Sol_Constructor

inputs_data = "Toys/Not Annotated/973.inst"

inputs = load_instance(inputs_data)

vehicles = {i+1: Vehicles(vehicle_id=veh[0], initial_battery=veh[1]) for i, veh in enumerate(inputs.vehicles)}

initial_solution = initial_solution(inputs, vehicles)