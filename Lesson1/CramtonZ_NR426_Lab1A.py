"""
This is Lab 1A for NR 426 based on the provided pseudocode. It was completed
following the PDF instructions provided through Canvas.

Goals:
*Update the header code with your own information
*Write well-commented, and readable code
*Choose short but descriptive variable names
*Rename this script file when you submit

NR 426 Lab 1A Code
Purpose: Learning Python Basics and practicing with variables, strings, numbers,
lists, and functions

Name: Zachary Cramton
Date: 22JAN2025

"""

# All import statements for modules go here:

"""
To import packages use:
Import packageName

Or

From packageName Import * (for all) or functionX (for a specific func)

For example: from math import *
"""
from os import *

#### In-class activities (DEMO)  ####

##  1. Create a variable for your name and return the length of your name
studentName = "Zachary Cramton"
nameLength = len(studentName) - 1

##  2. Create additional variables for these: Age, City you live in, Year you moved there, Current year
#      Then create a well-formatted string combining the above variables
#      Sample result: Cam the Ram is 65 years old. He has lived in Fort Collins for 65 years.
age = 21
city = "Fort Collins"
yearMoved = 2022
yearCurrent = 2026

#      Use basic math to determine your age when you arrived in that city and print a nicely formatted statement

yearsResident = yearCurrent - yearMoved

print (f"{studentName} is {age} years old and has lived in {city} for "
       f"{yearsResident} years since {yearMoved}.")

# Exploring len()

print (type(age))
print (type(studentName))
print (len(studentName))

# Indexing

"""
For indexing, try things out in the console before inserting into the code, 
in general the format is:

var[x:y]

With indexing from the left starting at 0 and indexing from the right starting at -1.
"""
#### Lab 1A Self-directed activities, done on your own  ####

##  3. Create two number variables, add them and print their sum
number1 = 5
number2 = 2

print (f"The sum is {number1 + number2}.")

##  4. Create a variable for your favorite elevation in feet (Fort Collins is 4980). Write the code to convert
#    that value into meters (just multiply by a conversion factor)
#    Create and print a well-formatted statement like 5280 feet is equal to 1604 meters

# Elevation of the Colorado low point on the Arikaree River

# Input elev
elevFT = 3317

# Unit Conversion (1 ft = 0.3048 m)
elevM = elevFT * 0.3048

# Print rounded value in an answer statement
print (f"The elevation of the Colorado low point on the Arikaree River is "
       f"{round(elevM)} meters or {elevFT} feet.")

##  5. Create a string variable and print with your own text to make a complete sentence
#    example: Create a variable for "Park_boundary.shp" ; sample result: The file name is Park_boundary.shp

# File name(s)
file1 = "Park_boundary.shp"

# Print file name
printFile = file1
print(f"The file name is {printFile}.")

##  6. Concatenate a number and a string variable using both str() and the f-string method.
#     Create a string and a number variable, then write the code to return a nicely formatted
#     sentence combining them twice: using str() then an f-string.
#     Add your own additional text as needed
#     (ex: Programming for GIS 1 is 8 weeks long)

# Course details
courseName = "Programming for GIS I"
courseDurationWk = 8

print (f"{courseName} is {courseDurationWk} weeks long.")

##  7. Work with index notation for a string (and recall that -1 indexes from the end)
#     a- Create a variable to represent a shapefile (just make something up): C:\student\NR426\LandCover.shp
fullPath = r"C:\Users\Zacha\College Classes\NR426\CO_Grassland.shp"

#     b- Write the code using index notation to parse out and print just the shapefile name without any path or extension
#     ex: The dataset name is: LandCover
print (f"The dataset name is {fullPath[-11:-4]}.")

#    c- Write the code using index notation to parse out and print just the file extension
#     ex: The file extension is .shp
print (f"The file extension is {fullPath[-4:]}.")

#    d-	Can you find another approach to splitting the file name from the path? (Hint: look in the os module)

# Splitting the file name using os.path.splitext()
sp1 = path.splitext(fullPath)
print (sp1)
print (f"The file extension is {sp1}.")

# Splitting the file name (and removing the extension) using fileName.split("delineator")
sp2 = fullPath.split("\\")
file2 = sp2[5]
print (f"The data name is {file2[:-4]}.")

##  8. Basic built-in functions
#    a-Use the appropriate function to determine and print out the -length- of
#     two of your previously created variables, in well formatted sentences.
print (f"The length of the path is {len(fullPath)} characters.")
print (f"The length of the file name is {len(file2)} characters.")

#    b- What -type- of object does the function you use above return? Use the correct function to return that information.
print (f"The len(), length function returns a {type(len(fullPath))} variable.")

#    c- Create a number variable with 4 decimals that represents a fictional area value for a polygon. (123.4567)
#       Write a print statement that dynamically reports the number, -rounded- to 2 decimal places (using the appropriate function),
#       along with other text. Sample result:
#       example result: The area of the open space is 123.46 acres
polyArea = 314.159
print (f"The area of the polygon is {round(polyArea, 2)} square meters.")

#  9. Importing and using the os module
#     The os library is quite useful for working with files.
#     Look into the os library https://www.geeksforgeeks.org/os-module-python-examples/ samples and write the code to:
#    a- Import the os library in the appropriate location in this script
       # Done, see line 32 for import.
#    b- Create a variable representing a file path (Copy your class folder path, remember to format the slashes or use r)
filePath = r"C:\Users\Zacha\PycharmProjects\NR426\Labs\Lab1"

#    c- Create a second variable representing the name of a potential dataset in that folder (like LandCover.shp)
dataName = "CO_WaterBodies.shp"

#    d-	Combine the path and file names into one complete string with correctly formatted slashes, using the os library
fileLocation = filePath + dataName