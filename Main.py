import re
from load_data import load_instance
from distance import distance

inputs_data = "/Users/rez/Documents/Engineering/PhD/Courses/04_DCA/Toys/Not Annotated/929.inst"

Inputs = load_instance(inputs_data)

print(distance(Inputs.customers[2], Inputs.customers[1]))
