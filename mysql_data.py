'''
This Python Code will be the one which dynamically stores the data of the Wemo
Switch when it is executed. The data is stored on average every 2-3 seconds.
'''

# PYMYSQL MODULES
import pymysql
import pymysql.cursors

# OUIMEAUX MODULES
import ouimeaux
from ouimeaux.environment import Environment
from ouimeaux.signals import receiver, statechange, devicefound

# Connect to the database
connection = pymysql.connect(host="localhost",
                             user='root',
                             passwd='ditpwd',
                             db="DATA")

# Initializing the ouimeaux environment
env = Environment()

class DATA:
    
    def kv_pairs(self,dict):
        '''OBTAINING THE KEY-VALUE PAIR PARAMATERS'''
        '''this function will be used to seperate
        key-value pairs in the dictionary for inserting
        data into MYSQL'''
        
        keys = str(list(dict.keys()))[:].replace('[', '(').replace(']', ')')
        vals = str(list(dict.values()))[:].replace('[', '(').replace(']', ')')
        
        keys = keys.replace("'","")
        vals = vals.replace("'","")
        return keys,vals
        
    def SWITCH(self,list_switches):
        
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
    
    def CREATE_DATA(self):
        
        try:
            # Commit every data as by default it is False
            connection.autocommit(True)
            
            # Create a cursor object
            cursorObject = connection.cursor()  
            
            env.start()
            env.discover(3)
                
            '''using MYSQL functions to insert date and time
            USEFUL FUNCTIONS IN MYSQL:
            CURRENT_TIMESTAMP
            CURRENT_DATE
            CURRENT_TIME
            '''
            try:
                env.start()
                env.discover(5)
                
                while True:
                    
                    for i in range(len(env.list_switches())):
                        
                        #Calling the helper function
                        switch = self.SWITCH(list(env.list_switches())[i])
                        
                        # Obtaining the switch parameters
                        switch_name = switch[0]
                        switch_wemo = switch[1]
                        
                        # Note: Parameters are stored in dictionary
                        switch_param = switch[2]
                        
                        keys = self.kv_pairs(switch_param)[0]
                        vals = self.kv_pairs(switch_param)[1]
                
                        print('------------')
                        print('Retrieving Data')
                        print('------------')
                        
                        # 1 indicates switch is on and load is on
                        if switch_wemo.get_state() == 1:
                            #print("name:",SWITCH,"STATE:ON")
                            insertStatement = ("INSERT INTO DATA_"+switch_name+
                                            "(DATE,TIME,STATE)"
                                            "VALUES(CURDATE(),CURTIME(),\"S:ON  | L:ON\")")
                            cursorObject.execute(insertStatement)
                            
                        # 8 indicates switch is on but load is off 
                        elif switch_wemo.get_state() == 8:
                            #print("name:",SWITCH,"STATE:ON")
                            insertStatement = ("INSERT INTO DATA_"+switch_name+
                                            "(DATE,TIME,STATE)"
                                            "VALUES(CURDATE(),CURTIME(),\"S:ON  | L:OFF\")")
                            cursorObject.execute(insertStatement)
                            
                        # 0 indicates switch if off 
                        else:
                            #print("name:",SWITCH,"STATE:OFF")
                            insertStatement = ("INSERT INTO DATA_"+switch_name+
                                            "(DATE,TIME,STATE)"
                                            "VALUES(CURDATE(),CURTIME(),\"S:OFF | L:OFF\")")
                            cursorObject.execute(insertStatement)
                        
                        #inserting new params
                        cursorObject.execute('INSERT INTO ' +switch_name+ ' %s VALUES %s' % (keys, vals))
                        env.wait(1)
                    
            except (KeyboardInterrupt, SystemExit):
                print("Goodbye!")
                
        except Exception as e:
            print("Exeception occured:{}".format(e))
            pass 
            
        finally:
            
            connection.close()

if __name__ == '__main__':
    
    DATA = DATA()
    DATA.CREATE_DATA()
