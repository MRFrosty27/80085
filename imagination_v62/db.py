import sqlite3
import os
db_name,db_connection,db_cursor = None,None,None
process_db_connection = None
process_db_cursor = None

def access_database(DB_name):
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

#table creation
def table_get_all():
    db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = db_cursor.fetchall()
    table_names = [t[0] for t in tables]
    #remove first 2 tables that are for the SQL config
    table_names.pop(0)
    table_names.pop(0)
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

def table_object_create():#creates the tables where the user will add components
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS main (
            X_cord INTEGER, 
            Y_cord INTEGER, 
            operation INTEGER
        )
    """
    create_index = "CREATE INDEX index_cord ON main (X_cord,Y_cord)"
    db_cursor.execute(create_table_query)
    db_cursor.execute(create_index)
    db_connection.commit()
    #print("end: create table")#use fore debug

def table_interconnect_create():#creates a mandatory table that defines how bits travel
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
    create_index = "CREATE INDEX index_path ON interconnect (inx,iny, outx, outy)"
    db_cursor.execute(query)
    db_cursor.execute(create_index)
    db_connection.commit()
    #print("end: create interconnect table")#use fore debug

def table_volitile_memory_create():#user creates a table that store data about RAM and CACHE
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
    db_cursor.execute(query)
    db_connection.commit()

#project interaction
def init_process_connection(db_path):
    global process_db_connection,process_db_cursor
    process_db_connection = sqlite3.connect(
        db_path,
        timeout=30,
        check_same_thread=False,     # ← very important for multiprocessing
        isolation_level=None         # ← auto-commit mode (recommended)
    )
    process_db_cursor = process_db_connection.cursor()
    process_db_cursor.execute("PRAGMA journal_mode=WAL")
    process_db_cursor.execute("PRAGMA synchronous=NORMAL")     # optional: faster

def project_create(project_name,processor_clock_speed,creation_date,last_accessed,last_modified):
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
    db_connection.commit()

def database_get_all_project_names():
    db = access_database("names_of_all_databases")
    db[1].execute(f"SELECT * FROM database_names")
    return db[1].fetchall()

def interconnect_add(inx,iny,outx,outy,inslot,outslot):
    query = f"""
    INSERT INTO interconnect (
    inx ,
    iny ,
    outx ,
    outy,
    inslot INTEGER,
    outslot INTEGER
    )
    VALUES (?,?,?,?)
    """
    db_cursor.execute(query,(inx,iny,outx,outy,inslot,outslot))
    db_connection.commit()

def object_add(X_cord,Y_cord,operation):#get called when a user adds a new gate 
    syntax = f"""
    INSERT INTO main (X_cord,Y_cord,operation) 
    VALUES (?,?,?)
    """
    db_cursor.execute(syntax,(X_cord, Y_cord, operation))
    db_connection.commit()

def object_load(X_cord,Y_cord,parallelism = False):#gets called when GUI needs to know which gate to display
    if parallelism == False:
        db_cursor.execute(f"SELECT * FROM main WHERE X_cord = ? AND Y_cord = ?;", (X_cord, Y_cord))
        result = db_cursor.fetchone()
        if result != None:
            return result[2]#output operation
        else:return 0
    else:
        global process_db_cursor
        if process_db_cursor is None: raise RuntimeError('process connection was not defined in func arg')
        process_db_cursor.execute(f"SELECT * FROM main WHERE X_cord = ? AND Y_cord = ?;", (X_cord, Y_cord))
        result = process_db_cursor.fetchone()
        if result != None:
            return result[2]#output operation
        else:return None

def object_update_cord(table,X_cord,Y_cord):#if the user moves gate to a diff pos
    update_X = f"""
    update {table}
    set X_cord = ? AND Y_cord = ?
    WHERE X_cord = ? AND Y_cord = ?;
    """
    db_cursor.execute(update_X,(X_cord,Y_cord))
    db_connection.commit()

def object_search_connected(inx,iny):
    #seach if two gate have existing interconnect connected
    db_cursor.execute("SELECT * FROM interconnect WHERE inx = ? AND iny = ? OR outx = ? AND outy = ?;", (inx,iny,inx,iny))
    return db_cursor.fetchone()
    
def object_remove(x,y):
    db_cursor.execute(f"DELETE FROM main WHERE X_cord = ? AND Y_cord = ?;", (x,y))
    db_connection.commit()

def interconnect_remove(x,y):
    db_cursor.execute(f"DELETE FROM interconnect WHERE inx = ? AND iny = ? ;", (x,y))
    db_cursor.execute(f"DELETE FROM interconnect WHERE outx = ? AND outy = ?;", (x,y))
    db_connection.commit()

def project_delete(project_name):
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
    db_connection.commit()

def add_volatile_memory(table,x,y,bandwidth,transfere_speed,space,stack_direction,name):
    mem = open(f"{name}.py")#creates a python file to store information and simple execution