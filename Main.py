import re
from load_data import load_instance
from distance import distance
from initial_solution import initial_solution
from find_nearest_charger import find_nearest_charger
from find_nearest_customer import find_nearest_customer

inputs_data = "/Users/rez/Documents/Engineering/PhD/Courses/04_DCA/Toys/Not Annotated/929.inst"

Inputs = load_instance(inputs_data)

Init_Solution = initial_solution(Inputs)


print(distance(Inputs.customers[2], Inputs.customers[1]))