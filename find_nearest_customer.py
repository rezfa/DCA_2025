# this function finds the nearest customer from current location

def find_nearest_customer(source, unvisited_customers, Inputs):
    return min(
        (customer for customer in Inputs.customers if customer[0] in unvisited_customers),
        key=lambda c: distance(source, c)
    )
