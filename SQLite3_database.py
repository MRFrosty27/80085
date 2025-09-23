import sqlite3
import os

db_name = None
#add:sqlite indexing for big O(1) read speeds
def access_database(DB_name):#warning: when this func is executed from this file it will return an error as the path will be .../databases/projects rather than .../projects
    path = os.path.join(os.path.dirname(__file__),"projects")
    if os.path.exists(path):
        try:
            connection = sqlite3.connect(os.path.join(path,f"{DB_name}.db"))
            cursor = connection.cursor()
            return connection, cursor
        except:
            print("db could not be access or created as path is incorrect")
    else:
        print(f"path:{path} does not exist")
    

def close_database():
    if type(db_name) != None:
        db_name[1].commit() 
        db_name[0].close()

#table creation
def get_all_table_names():
    #print("Start: get all table names")#use fore debug
    db_name[1].execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = db_name[1].fetchall()
    table_names = [t[0] for t in tables]
    #remove first 2 tables that are for the SQL config
    table_names.pop(0)
    table_names.pop(0)
    #print(table_names)
    #print("End: get all table names")#use for debug
    return table_names

def create_table_of_database_names():#only needes to be performed once when user installs software
    DB_name = access_database("names_of_all_databases")#creates new database
    create_table_query = """
        CREATE TABLE IF NOT EXISTS database_names (
            database_name TEXT,
            processor_clock_speed INTEGER,
            creation_date TEXT,
            last_accessed TEXT,
            last_modified TEXT
        )
    """
    DB_name[1].execute(create_table_query)
    DB_name[0].commit()

def create_table():#creates the tables where the user will add components
    #print("Start: create table")#use fore debug
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS main (
            X_cord INTEGER, 
            Y_cord INTEGER, 
            operation INTEGER
        )
    """
    db_name[1].execute(create_table_query)
    db_name[0].commit()
    #print("end: create table")#use fore debug

def create_inteconnect_table():#creates a mandatory table that defines how bits travel
    #print("start: create interconnect table")#use fore debug
    query = f""" 
    CREATE TABLE IF NOT EXISTS interconnect (
        inx INTEGER,
        iny INTEGER,
        outx INTEGER,
        outy INTEGER,
        inslot INTEGER,
        outslot INTEGER
    )
    """#slot: 0-top left, 1-top right, 2-bottom left, 3-bottom right
    db_name[1].execute(query)
    db_name[0].commit()
    #print("end: create interconnect table")#use fore debug

def create_volitile_memory_table():#user creates a table that store data about RAM and CACHE
    query =f"""
    CREATE TABLE IF NOT EXISTS volitile_memory (
    name TEXT,
    bandwidth INTEGER,
    output INTEGER,
    transfere_speed INTEGER,
    space INTEGER,
    X_cord INTEGER,
    Y_cord INTEGER,
    stack_direction X_cord INTEGER
    )
    """
    db_name[1].execute(query)
    db_name[0].commit()

def create_start_table():#creates a table that defines where the starts
    #print("start: creat start table")#use fore debug
    db_name[1].execute("CREATE TABLE IF NOT EXISTS start (X_cord INTEGER,Y_cord INTEGER,state INTEGER)")
    db_name[0].commit()
    #print("end: create start table")#use fore debug



#project interaction
def add_database_name(project_name,processor_clock_speed,creation_date,last_accessed,last_modified):
    query = f"""
    INSERT INTO database_names (
    database_name,
    processor_clock_speed ,
    creation_date ,
    last_accessed ,
    last_modified 
    )
    VALUES (?,?,?,?,?)
    """
    DB_name = access_database("names_of_all_databases")
    DB_name[1].execute(query,(project_name,processor_clock_speed,creation_date,last_accessed,last_modified))
    DB_name[0].commit()

def get_all_database_names():
    db = access_database("names_of_all_databases")
    db[1].execute(f"SELECT * FROM database_names")
    return db[1].fetchall()

def add_interconnect(inx,iny,outx,outy):
    #print("start: add interconnect")#use fore debug
    query = f"""
    INSERT INTO interconnect (
    inx ,
    iny ,
    outx ,
    outy 
    )
    VALUES (?,?,?,?)
    """
    db_name[1].execute(query,(inx,iny,outx,outy))
    db_name[0].commit()
    #print("end: add interconnect")#use fore debug

def add_starting_point(x,y):#adds a starting point in staring point table
    #print("start: add starting point")#use fore debug
    query = f"""
    INSERT INTO start (
    X_cord ,
    Y_cord ,
    state
    )
    VALUES(?,?,?)
    """
    db_name[1].execute(query,(x,y,1))
    db_name[0].commit()
    #print("end:add starting point")#use fore debug

def user_add_object(X_cord,Y_cord,operation):#get called when a user adds a new gate 
    #print("start: user add object")#use fore debug
    syntax = f"""
    INSERT INTO main (X_cord,Y_cord,operation)
    VALUES (?,?,?)
    """
    db_name[1].execute(syntax,(X_cord, Y_cord, operation))
    db_name[0].commit()
    #print("end: user add object")#use fore debug

def load_object(X_cord,Y_cord):#gets called when GUI needs to know gate to display
    #print("start: load object")#use fore debug
    db_name[1].execute(f"SELECT * FROM main WHERE X_cord = ? AND Y_cord = ?;", (X_cord, Y_cord))
    result = db_name[1].fetchone()
    return result
        
def update_cord(table,X_cord,Y_cord):#if the user moves gate to a diff pos
    #print("start: update cord")#use fore debug
    update_X = f"""
    update {table}
    set X_cord = ? AND Y_cord = ?
    WHERE X_cord = ? AND Y_cord = ?;
    """
    db_name[1].execute(update_X,(X_cord,Y_cord))
    db_name[0].commit()
    #print("end: update cord")#use fore debug

def update_operation(X_cord,Y_cord,new_operation):#if a user replace gate with another on the same pos
    #print("start: update operation")#use fore debug
    query = f"""
    update main
    set operation = ?
    where X_cord = ? AND Y_cord = ?;
    """
    db_name[1].execute(query,(new_operation,X_cord,Y_cord))
    db_name[0].commit()
    #print("end: update operation")#use fore debug

def get_op(table,ID):#used when simulation is being prepared.
    db_name[1].execute(f"SELECT * FROM {table} WHERE ID = ?;", (ID))
    result = db_name[1].fetchone()
    return result[0]

def search_if_connected(inx,iny,outx,outy):
    #seach if two gate have existing interconnect connected
    db_name[1].execute("SELECT * FROM interconnect WHERE inx = ? AND iny = ? AND outx = ? AND outy = ?;", (inx,iny,outx,outy))
    if db_name[1].fetchone() is not None:
        return True
    
def search_SP(x,y):
    #search if a starting point exists
    db_name[1].execute("SELECT * FROM start WHERE X_cord = ? AND Y_cord = ? ;", (x,y))
    return db_name[1].fetchone()

def remove_object(x,y):
    db_name[1].execute(f"DELETE FROM main WHERE X_cord = ? AND Y_cord = ?;", (x,y))
    db_name[0].commit()

def remove_SP(x,y):
    db_name[1].execute(f"DELETE FROM startingPoint WHERE X_cord = ? AND Y_cord = ?;", (x,y))
    db_name[0].commit()

def remove_interconnect(x,y):
    db_name[1].execute(f"DELETE FROM interconnect WHERE inx = ? AND iny = ? ;", (x,y))
    db_name[1].execute(f"DELETE FROM interconnect WHERE outx = ? AND outy = ?;", (x,y))
    db_name[0].commit()

def del_project(project_name):
    print(project_name)
    #delete DB file
    path = os.path.join(os.path.dirname(__file__),"projects")
    if os.path.exists(path):
        path = os.path.join(path,f"{project_name}.db")
        if os.path.isfile(path):
            os.remove(path)
        else:
            print("file does not exist")
    else:
        print(f"path:{path} does not exist")
    #remove project name from record
    DB_name = access_database("names_of_all_databases")
    DB_name[1].execute(f"DELETE FROM database_names WHERE database_name = ?;",(project_name,))
    DB_name[0].commit()

def add_volatile_memory(table,x,y,bandwidth,transfere_speed,space,stack_direction,name):
    mem = open(f"{name}.py")#creates a python file to store information and simple execution
    
def change_starting_point_bit(x,y):
    query = """
    update startingPoint
    set state = ?
    WHERE X_cord = ?
    AND Y_cord = ?;
    """
    db_name[1].execute("SELECT * FROM startingPoint WHERE X_cord = ? AND Y_cord = ? ;", (x,y))
    bit = db_name[1].fetchone()
    if bit == 0:
        db_name[1].execute(query,1)
    elif bit == 1:
        db_name[1].execute(query,0)

def get_gate_table(x,y):#used when adding an interconnect
    table_names = get_all_table_names(db_name[1])
    table_names.remove("interconnect")
    table_names.remove("sqlite_sequence")
    table_names.remove("startingPoint")
    for table in table_names:#search through all tables for the gate
        db_name[1].execute(f"SELECT * FROM {table} WHERE X_cord = ? AND Y_cord = ?;", (x, y))
        if db_name[1].fetchone() is not None:
            return table
    return None

def get_interconnect_slot(inx,outx,iny,outy):
    db_name[1].execute("SELECT * FROM interconnect WHERE inx = ? AND outx = ? AND iny = ? AND outy = ?",(inx,outx,iny,outy))
    interconnect = db_name[1].fetchone()
    return interconnect[-2],interconnect[-1]

#the following defines the different gates
def AND_gate(input1,input2):
    if input1 == True and input2 == True:
        return True
    else:
        return False

def OR_gate(input1,input2):
    if input1 == False and input2 == False:
        return False
    else:
        return True

def NAND_gate(input1,input2):
    if input1 == False and input2 == False:
        return True
    else:
        return False

def XOR_gate(input1,input2):
    if input1 == True and input2 == True:
        return False
    else:
        return True

def default_config():#creates the default gates when a new project is created
    Table = "start"
    #creates the default layout
    create_table(Table)
    user_add_object(Table,0,0,1,None)
    object = load_object(Table,0,0)
    #creates the default interconnects
    create_inteconnect_table()

