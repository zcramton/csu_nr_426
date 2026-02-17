"""
Header Code:
NR426 - Programming for GIS 1
Lesson 1B Pre-Class Demo - Lists and Loops

Zachary Cramton - 27JAN2026
"""
print ("Starting List Script\n")
# Import necessary libs
import os

# Declare Vars
# City to add to list
FC = ("Fort Collins")

# City to remove from list
LV = "Loveland"

# Create a list of cities
cities = ["wellington", "Greeley", "Loveland", "Longmont", "Boulder"]

print ("Printing just the list:")
print (cities)

# Print out a well formatted list, sequentially numbered.
cities.append(FC)
cities.remove(LV)

print ("Printing it nicer:")
ctr = 1
for eachitem in cities:
    print ("City Name {0}: ".format(ctr) + eachitem)
    ctr += 1

# Create a new variable for an address - Street, City, State
addr = "101 S. College Ave, Fort Collins, CO"

# Use split to parse out the city name
add_list = addr.split(", ")
print (add_list)
StreetAddr = add_list[0]
print(StreetAddr)

print (add_list[1])

print ("\n - - - List Script Completed - - -")
