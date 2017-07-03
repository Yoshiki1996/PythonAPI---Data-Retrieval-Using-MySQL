'''
This Python Code generates the graphs of Currentpower vs. Time.
There are three graphs:

MAKE_PLOT(X,Y):
This plots the currentpower vs. time from the original set of data. This may
not be optimal if one wants to minimize the amount of data sets for optimizing
memory space

PLOT_FINALDATA_SMOOTHING(X,Y):
This plots the currentpower vs. time first smoothing out the original data set.
The maximum value is then stored using argmax which will be a reference point to 
be connected. This will reduce the amount of dataset although if one wants to 
keep the currentpower drained by the appliance as is, then it may not be optimal.

PLOT_FINALDATA(X,Y):
This plots the currentpower vs. time first storing the point where 
currentpower = 0[W]. It will neglect all the other points with 0[W] until there
is a change in current - this interval will then be stored. It is the same plot#
as MAKE_PLOT(X,Y) reducing the amount of unnecessary data.

'''

# NUMPY MODULES 
import numpy as np

# PYMYSQL MODULES
import pymysql
import pymysql.cursors

# OUIMEAUX MODULES
import ouimeaux
from ouimeaux.environment import Environment
from ouimeaux.signals import receiver, statechange, devicefound

# MATPLOTLIB MODULES
import matplotlib.pyplot as plt

# PLOTLY and PANDAS MODULES 
import plotly
import pandas
from plotly.graph_objs import *

# NUMPY MODULES
import numpy as np

# SCIPY MODULES
from scipy.interpolate import spline
from scipy.interpolate import interp1d
from scipy.signal import argrelextrema

# Initializing the ouimeaux environment
env = Environment()

'''SIDENOTES
In order to access a certain column of interest the
Mysql syntax is: select column from table

TABLE STRUCTURE:
In order to store the current data, we have the time axis. There are
different time interval readings between each successive data. Whenever
we store the current data, the time will start from a reference of 0 seconds.
The time interval between each reading will be used from the stored query called,
'TIME_DIFF'

USEFUL MYSQL FUNCTIONS:
SELECT TIME_TO_SEC(TIMEDIFF('12:01:00', '12:00:00')) diff;
^ Gives the time difference in seconds
'''

# Connect to the database
connection = pymysql.connect(host="localhost",
                            user='root',
                            passwd='ditpwd',
                            db="DATA")

def empty(list):
    '''A simple function which checks if a list 
       is empty or not'''
    
    if len(list) == 0:
        return True 
    else:
        return False 

def np_empty(nparray):
    '''A simple function which checks if a numpy
       array is empty or not'''
       
    if np.array.size == 0:
        return True
    else:
        return False
        
def SWITCH(list_switches):
    '''This function intakes the list of switches
    and returns the attributes given by the environment
    NOTE: Returns a Tuple
    '''
    # Obtaining the switch parameters
    switch_name = list_switches
    switch_wemo = env.get_switch(switch_name)
    # Note: Parameters are stored in dictionary
    switch_param = switch_wemo.insight_params
    # Delete lastchange: Unnecessary Parameter
    switch_param.pop('lastchange')
    
    # Adding DATE and TIME dictionary to SWITCH_PARAM
    switch_param['TIME'] = 'CURTIME()'
    switch_param['DATE'] = 'CURDATE()'
    
    return switch_name,switch_wemo,switch_param
 
def TIME_IND(switch,last_index):
    '''This function will compute the time difference
    between each currentpower and store it in the table IND_Insight
    '''
    cursorObject = connection.cursor()  
    last_ind = str(last_index)
    
    # We must be careful not to keep on storing the same values
    ROW = "Select last_index from IND_" + switch[0]
    cursorObject.execute(ROW)
    prev_index = cursorObject.fetchall()
    
    if empty(prev_index) == True:
        insertStatement = ("INSERT INTO IND_"+switch[0]+"(last_index) "
                            "VALUES("+last_ind+")")
                            
        cursorObject.execute(insertStatement)
        
    elif prev_index[-1][0] == last_index:
        return 
        
    else:
        insertStatement = ("INSERT INTO IND_"+switch[0]+"(last_index) "
                            "VALUES("+last_ind+")")
                            
        cursorObject.execute(insertStatement)

def store_time_diff(time_rows):
    '''This function uses a list called time_rows which is a list
       that contains the rows of the times switch was on or off
    '''
    # Create a list to store the time differences
    time_del = []
    
    for j in range(len(time_rows)):
        if j == len(time_rows)-1:
            break
        else:
            # Fetch the time in the rows
            t1 = time_rows[j][0].seconds
            t2 = time_rows[j+1][0].seconds
            time_del.append(t2-t1)
    
    time_del.insert(0,0)
    return time_del

def store_currentpower(cp_rows):
    '''This function uses a list called time_rows which is a list
       contains the rows of the switches currentpower'''
    
    # Create a list to store the cp_rows
    currentpower = []
    
    for i in range(len(cp_rows)):
        currentpower.append(cp_rows[i][0]/1000)
    
    return currentpower

def MAKE_PLOT(time_del,current_power):
    '''A function which generates currentpower vs. time plot'''
    
    # Using matplotlib to plot currentpower[W] vs time[s]
    # Initialize these variables as X-Y 
    X = np.cumsum(time_del)
    Y = list(current_power)
    
    # Show plot
    plt.plot(X,Y)
    plt.ylabel('currentpower [W]')
    plt.xlabel('time [s]')
    plt.title('currentpower vs. time')
    plt.show()

def fetch_data(switch,start_index,end_index):
    '''Function used to fetch certain rows of data
        By default it fetches from the very recent to last'''
    
    # TIME DATA
    ROW = "Select TIME from " + switch[0]
    cursorObject.execute(ROW)
    time_rows = cursorObject.fetchall()
    time_rows = time_rows[start_index:end_index+1]
    time_del = store_time_diff(time_rows)
    
    # CURRENTPOWER DATA
    ROW = "Select currentpower from " + switch[0]
    cursorObject.execute(ROW)
    cp_rows = cursorObject.fetchall()
    cp_rows = cp_rows[start_index:end_index+1]
    current_power = store_currentpower(cp_rows)
    
    return time_del,current_power
    
def CONV_NPARRAY(x_list,y_list):
    '''simple function which converts lists to
       numpy arrays. Returns a tuple of X & Y'''
       
    X = np.array(x_list)
    Y = np.array(y_list)
    
    return X,Y
    

def CPT_SWITCH(switch):
    '''A function called twice within the try-exception statement. It's
       The one which compactly generates the plot'''
    
    # Rows are stored in a tuple
    ROW = "Select TIME from " + switch[0]
    cursorObject.execute(ROW)
    time_rows = cursorObject.fetchall()
    
    # A list which contains the difference between each successive time
    time_del = store_time_diff(time_rows)
    
    # CALL THE TIME_DIFF FUNCTION TO STORE THE LAST
    # USED INDEX
    TIME_IND(switch,len(time_del))
    
    # Fetching the currentpower Data 
    ROW = "Select currentpower from " + switch[0]
    cursorObject.execute(ROW)
    
    # Rows are stored in a tuple
    cp_rows = cursorObject.fetchall()
    
    # list containing currentpower 
    current_power = store_currentpower(cp_rows)
    
    # Generate actual plot
    MAKE_PLOT(time_del,current_power)
    # Generate plot
    # PLOT_FINALDATA(time_del,current_power)

### First approach in obtaining max and min values from smoothing out plot
def smooth(X,Y,spacing):
    '''This function returns the respective X and Y coordinates
       To smooth out the plot. Note that the coordinates are 
       converted to numpy arrays'''
       
    X = np.cumsum(X)
    Y = list(Y)
    XP,YP = CONV_NPARRAY(X,Y)
    XP_SMOOTH = np.linspace(XP.min(),XP.max(),spacing)
    YP_SMOOTH = spline(XP,YP,XP_SMOOTH)
    
    return XP_SMOOTH,YP_SMOOTH

def refined_data(XP,YP):
    '''This function takes the X-Y array coordinates which have 
       been smoothed out and stores the local max/min vals. It
       then after appends these such values in order to truncate
       values'''
    
    Y_IND_MIN = argrelextrema(YP, np.less)[0]
    Y_REFINED_MIN = YP[argrelextrema(YP, np.less)[0]]
    X_REFINED_MIN = np.array([XP[i] for i in Y_IND_MIN])
    
    Y_IND_MAX = argrelextrema(YP, np.greater)[0]
    Y_REFINED_MAX = YP[argrelextrema(YP, np.greater)[0]]
    X_REFINED_MAX = np.array([XP[i] for i in Y_IND_MAX])
    
    X_REFINED = np.append(X_REFINED_MIN,X_REFINED_MAX)
    Y_REFINED = np.append(Y_REFINED_MIN,Y_REFINED_MAX)
    
    return X_REFINED,Y_REFINED
    
def xintervals(XP,YP):
    '''This function takes the X and Y coordinates and
       stores the beginning and ending intervals intersecting
       the x-axis. However, we store all the values in 
       numpy array'''
    
    XY = []
    XY_TEMP = []
    XP = np.cumsum(XP)
    # Placeholders
    XP = np.append(XP,0)
    YP = np.append(YP,0)
    # First column: X # Seconds column: Y
    xy_pairs = np.vstack([XP,YP]).T
    
    i = 0
    while i < xy_pairs.shape[0]-1:
        if xy_pairs[i][1] == 0:
            # Store the first value where it hits
            # x-axis
            XY_TEMP.append((xy_pairs[i][0],xy_pairs[i][1]))
            #print(XY_TEMP)
            if xy_pairs[i+1][1] > 0:
                if 0 <= i < xy_pairs.shape[0]:
                    if i == 0:
                        XY.append(XY_TEMP[0])
                        XY_TEMP = []
                    else:
                        XY.append(XY_TEMP[0])
                        XY.append(XY_TEMP[-1])
                        XY_TEMP = []
                else:
                    pass
            
            elif i == xy_pairs.shape[0]-2 and XY_TEMP[-2][1] == 0:
                XY.append(XY_TEMP[0])
                XY.append(XY_TEMP[-1])
            
        i += 1
        
    return XY

def remove_xintervals(XP,YP):
    '''This function removes all the points with y=0. This will greatly
       reduce the data as many devices will not be on for most of the time,
       with the exception with fridges, etc.'''
    
    num_nonzeros = np.count_nonzero(YP)
    XP = np.cumsum(XP)
    XY_TEMP = np.vstack((XP,YP)).T
    XY_TEMP = XY_TEMP[np.argsort(XY_TEMP[:,1])]
    num_zeros = XY_TEMP.shape[0] - num_nonzeros
    
    # New X-Y plots without having values y=0
    XY_NEW = XY_TEMP[(num_zeros):XY_TEMP.shape[0]-(num_zeros-2)]
    
    return XY_NEW
    
def final_data(XP,YP):
    '''This function obtains the final data points using the smoothing 
       function, spline, provided by Python scipy module'''
       
    XP_SMOOTH,YP_SMOOTH = smooth(X,Y,200)
    X_REFINED,Y_REFINED = refined_data(XP_SMOOTH,YP_SMOOTH)
    XY_TEMP = np.vstack((X_REFINED,Y_REFINED)).T
    XY = np.array(xintervals(XP,YP))
    
    len_history = []
    i = XY_TEMP.shape[0]-1
    len_history.append(i)
    
    while i >= 0:
        # base case
        if i == XY_TEMP.shape[0]-1:
            
            if XY_TEMP[i][1] < 0:
                XY_TEMP = np.delete(XY_TEMP,i,axis = 0)
            else:
                pass
                
        else:
            if XY_TEMP[i][1] < 0:
                # Check if the update is the same as the previous length.
                # If it is, then it must mean there are no more values to 
                # remove.
                if len_history[-1] == len_history[-2]:
                    break
                else:
                    XY_TEMP = np.delete(XY_TEMP,i,axis = 0)
                    len_history.append(XY_TEMP.shape[0])
            else:
                pass
        
        len_history.append(i)
        i -= 1
            
    # Gathering all the refined data
    # There are three cases we have to keep in mind:
    if XY.shape[0] == 0:
        return XY_TEMP
    elif XY_TEMP.shape[0] == 0:
        return XY
    else:
        return np.vstack((XY,XY_TEMP))

def PLOT_FINALDATA_SMOOTHING(XP,YP):
    '''function which plots the points using python spline'''
    
    XY = final_data(XP,YP)
    x,y = XY[np.argsort(XY[:,0])].T
    # print((XY[np.argsort(XY[:,0])].T).shape[1])
    plt.plot(x,y)
    plt.ylabel('currentpower [W]')
    plt.xlabel('time [s]')
    plt.title('currentpower vs time')
    plt.show()

def PLOT_FINALDATA(XP,YP):
    
    XY1 = xintervals(XP,YP)
    XY2 = remove_xintervals(XP,YP)
    XY = np.vstack((XY1,XY2))
    x,y = XY[np.argsort(XY[:,0])].T
    # print((x,y))
    plt.plot(x,y)
    plt.ylabel('currentpower [W]')
    plt.xlabel('time [s]')
    plt.title('currentpower vs time')
    plt.show()

try:
    # Start the ouimeaux environment
    env.start()
    env.discover(3)
    
    # Commit every data as by default it is False
    connection.autocommit(True)
    
    # Create a cursor object
    cursorObject = connection.cursor()  
    
    # We will have to iterate through each available switch
    for i in range(len(env.list_switches())):        
        
        switch = SWITCH(list(env.list_switches())[i])
        
        # Rows are stored in a tuple
        ROW = "Select last_index from IND_" + switch[0]
        cursorObject.execute(ROW)
        index_rows = cursorObject.fetchall()
        
        if empty(index_rows) == True or len(index_rows) == 1:
            ''' This part of the code only executes once - when we generate a plot
            the first time'''
            #print('hi')
            CPT_SWITCH(switch)
            
        else:
            ''' This part of the code is executed every time after the first if
            statement'''
            
            ROW = "Select TIME from " + switch[0]
            cursorObject.execute(ROW)
            end_index = len(cursorObject.fetchall())
            TIME_IND(switch,end_index)
            
            ROW = "Select last_index from IND_" + switch[0] 
            cursorObject.execute(ROW)
            
            # Initiate the starting index to whatever is needed
            start_index = cursorObject.fetchall()[-2][0]
            
            # Generate the plot from the last stored value
            X,Y = fetch_data(switch,start_index,end_index)
            
            ###
            # Generate the plot which gives the smooth curves
            
            # XP_SMOOTH,YP_SMOOTH = smooth(X,Y,200)
            # plt.plot(XP_SMOOTH,YP_SMOOTH)
            # plt.show()
            
            ###
            
            
            
            ### 
            # Generate the points where the max/min values lie from the 
            # Smoothed out curve.
            
            # X_REFINED,Y_REFINED = refined_data(XP_SMOOTH,YP_SMOOTH)
            # plt.plot(X_REFINED,Y_REFINED,'ro')
            # plt.plot(XP_SMOOTH,YP_SMOOTH)  
              
            ###
            
            
            
            ###
            # Generate the actual plot from the Wemo Devices
            
            # MAKE_PLOT(X,Y)
            
            ###
            # Generate the final plot using the spline function
            
            # PLOT_FINALDATA_SMOOTHING(X,Y)
            
            ###
            
            ###
            # Generate the final plot containing all the ON state points
            # and only the beginning and ending points when currentpower = 0
            
            PLOT_FINALDATA(X,Y)
            
            ###
                
except Exception as e:
    
    print("Exeception occured:{}".format(e))
    
    
    
    
    
    