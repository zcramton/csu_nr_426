"""
This is Lab 1B for NR 426 based on the provided pseudocode. It was completed
following the PDF instructions provided through Canvas.

*Update the header code with your own information
*Write well-commented, and readable code
*Choose short but descriptive variable names
*Rename this script file when you submit it to read NR426 Lab 1B yourlastname.py

NR 426 Lab 1B Code
Purpose: Learning Python Basics and practicing with lists, looping, if, try

Name: Zachary Cramton
Date: 22JAN2025

"""

# All import statements for modules go here:

#### In-class activities (DEMO) (goes with Lesson 1B)  ####

#  1.	Determine the longest name in a list of names
#       Create a list of students’ names (choose 5-10 names)
#    	Loop through each name, determine the length of each
#    	Determine the max length (use if or the max function)
nameList = ["Zachary", "Ronan", "Sam", "Issac", "Gavin"]
for name in nameList:
    # print(name) # Print each name in the list
    print(f"{name} - {len(name)}") # Print "name" - "name length"

print(max(nameList)) # Returns the name from the list starting with the last alphabetical letter
print(max(nameList, key = len)) # Returns longest name in list

#  In a geospatial context, imagine it’s a list of numbers that represent area, year, or coordinates,
#  and you’re looking for the largest feature, or the newest feature.

#  2.	Explore the random module - randomly select a winner from your above list object
#   	Randomly select 3 people as 1st, 2nd, and 3rd place “winners” and print out the result with
#   	complete sentences
import random
winner = random.choice(nameList)
print(f"The winner is {winner}")

#In a geospatial context, you may need to randomly select a certain number of features for sampling.

#### Self-directed actvities, done on your own (goes with Lesson 1B) ####
## *** IMPORTANT: Refer to the Lab 1B instructions for all the details for this part ***


#  3 - Create a list and perform multiple operations on it. Use the result of one operation as input to the next
# (The list will keep changing). Refer to the instructions, write the code, print the result, and ADD your
# own EXPLANATION of what the operation is doing
parkList = ["Horsetooth", "Lory", "Maxwell", "RMNP"]

#  3a - len
print ("3a)")
print (len(parkList)) # This returns the length of the list of parks (len = 4)

#  3b - mylist[2]
print ("3b)")
print (parkList[2]) # This returns the 3rd list item (2 counts as 3 indexed from 0).

#  3c - mylist[1:]
print ("3c)")
print (parkList[1:]) # This returns a new list sliced from parkList starting at index position 1.

#  3d - mylist [1]
print ("3d)")
print (parkList[1]) # This returns only position 1 from parkList

#  3e - mylist.index()
print ("3e)")
print (parkList.index("Lory")) # Prints the index position of "Lory" in the list order

#  3f - mylist.pop()
print ("3f)")
print (parkList.pop(1)) # Removes the item in list index 1 and prints it.

#  3g - mylist.append()  <--Append a new park value like "Greyrock" or something of your choice
print ("3g)")
parkList.append("Greyrock") # Adds Greyrock to the parkList
print(parkList)             # Prints new parkList, to confirm successful .append()

#  3h - mylist.sort()  <-- Can't print this. Run sort, then print sorted list in another line
print ("3h)")
parkList.sort(reverse=True) # Sorts park list
print (parkList)            # Prints the park list sorted backwards by alphabetical order

# 4 - Looping through a list, starting simple and building complexity
#  4a - Loop through a basic list
#  4b - Add the length of each string to the print statement
#  4c - Alphabetize the list, and still include the length
#  4d - Sequentially number the list using code, and still have it alphabetized with the length
# Refer to the lab instructions for details. You can just provide the completed code for "d" since the tasks build on one another

# Building the state list
fcStatesList = ["Colorado", "New Mexico", "Utah", "Arizona"]

# Print the initial list with a for loop
print ("The Four Corners States are:")
for state in fcStatesList:
    print(state)

# Print the states with length using a loop
print ("The Four Corners States are:")
for state in fcStatesList:
    print (f"{state} - {len(state)}")

# Alphabetize the list with .sort()
print("The Four Corners States are:")
fcStatesList.sort()
for state in fcStatesList:
    print (f"{state} - {len(state)}")

# Number each item on the list with a loop
print("The Four Corners States are:")
for state in fcStatesList:
    print (f"{fcStatesList.index(state) + 1}. {state} - {len(state)}")


#### Lesson 1C: More In-class activities (DEMO)  ####

#  5 - Practicing with an if statement and multiple conditions. Use variables, add comments.


#  6 - Break the code above and have a neighbor spot the errors


#  7 - Look at sample code with instructor on screen - update file paths, experiment with creating string outputs
# Nothing to submit for this step.






####Lesson 1C:  More Self-directed actvities, done on your own  ####


#  8 - Manipulating strings to prepare file names
#      Create a list object for <fictional> shapefile names. Write the code to parse and format each shapefile
#      name to represent what it will need to be called when imported into a geodatabase: remove .shp extension,
#     combine with the path, and capitalize the file name
#     Refer to the Lab 1 instructions for details, hints, and examples





#  9 - Create a string variable (ie, for a land cover type) and examine it for the occurrence of a particular word.
#       Use an if statement to return a message to the user if the word is in the variable or not
#       You’ll need to find/search for the function that does this. In a comment, provide what you searched on,
#       and what website gave you the answer
#      Refer to the Lab 1 instructions for details and hints




#  10 - Working with filenames and paths
#   a - Write the code to determine if a file or folder exists or not, by creating a string variable for
#        a file/path name and using the appropriate os module method and an if statement.
#   b - Return the result in a well formatted sentence.
