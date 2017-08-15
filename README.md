# PythonAPI---Data-Retrieval-Using-MySQL

Using Wemo Smart Switches to retrieve the data such as the state of the appliance,
current drained by the appliance, dates the appliance was one for, etc. and storing
it in a MySQL database. These data will then be used to generate plots. mysql_plot
specifically plots the current drained by the appliance vs. time. 

mysql_table: Retrieves all available appliances using Wemo Switch and generates table
             in MySQL
             
mysql_data: Retrieves all information such as state, currentpower, total on time, etc.
            and stores it into the respective tables in MySQL real-time.
            
mysql_plot: Retrieves the data and plots currentpower vs. time

# Requirements:
1) Python Version 3 or higher
2) A database named, 'DATA' in MySQL

Modules:
1) Numpy
2) Scipy
3) Ouimeaux
Note: all modules are commented and explained within the python files
