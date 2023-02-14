# -*- coding: utf-8 -*-
"""
The objective of this program is to create a SQL database with a series of 
tables defined by the schemas given by the function create_schemas and populate
the different tables with the CSV files obtained from the program osm2csv.

The code is based on the one from this source:
    https://www.sqlitetutorial.net/sqlite-python/create-tables/

The schemas are defined based on the repository referenced in the Udacity's 
project details:
    https://gist.github.com/swwelch/f1144229848b407e0a5d13fcb7fbbd6f

Python version: 3.6.0
"""

import re
import sqlite3
import pandas as pd


def create_schemas(nodes_path, node_tags_path, ways_path, way_nodes_path, 
                   way_tags_path):
    """Define the required schemas for the creation of the different tables
       in the SQL database and store them in a dictionary"""
    
    schemas = {}
    schemas[nodes_path] = """CREATE TABLE nodes (
                             id INTEGER PRIMARY KEY NOT NULL,
                             lat REAL,
                             lon REAL,
                             user TEXT,
                             uid INTEGER,
                             version INTEGER,
                             changeset INTEGER,
                             timestamp TEXT
                             );"""
    schemas[node_tags_path] = """CREATE TABLE nodes_tags (
                                 id INTEGER,
                                 key TEXT,
                                 value TEXT,
                                 type TEXT,
                                 FOREIGN KEY (id) REFERENCES nodes(id)
                                 );"""
    schemas[ways_path] = """CREATE TABLE ways (
                            id INTEGER PRIMARY KEY NOT NULL,
                            user TEXT,
                            uid INTEGER,
                            version TEXT,
                            changeset INTEGER,
                            timestamp TEXT
                            );"""
    schemas[way_tags_path] = """CREATE TABLE ways_tags (
                                 id INTEGER NOT NULL,
                                 key TEXT NOT NULL,
                                 value TEXT NOT NULL,
                                 type TEXT,
                                 FOREIGN KEY (id) REFERENCES ways(id)
                                 );"""
    schemas[way_nodes_path] = """CREATE TABLE ways_nodes (
                                id INTEGER NOT NULL,
                                node_id INTEGER NOT NULL,
                                position INTEGER NOT NULL,
                                FOREIGN KEY (id) REFERENCES ways(id),
                                FOREIGN KEY (node_id) REFERENCES nodes(id)
                                );"""
    
    return schemas


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def create_connection(db_file):
    """Creates a connection to a SQL file"""
    
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn


def create_table(conn, sql_schema):
    """Creates a new table in the SQL file with a given schema"""
    
    table_name = re.search("CREATE TABLE (\w+)", sql_schema).group(1)    
    try:
        c = conn.cursor()
        c.execute(sql_schema)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    
    return table_name


def import_csv(conn, csv_file, table_name):
    """Imports a CSV file into the corresponding SQL table"""
    
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    conn.commit()


# ================================================== #
#               Main Function                        #
# ================================================== #
def create_database(db_path, nodes_path, node_tags_path, ways_path, 
                    way_nodes_path, way_tags_path):
    """Creates a SQL database with the defined schemas and imports the data
       from CSV files"""
    
    sql_table_schemas = create_schemas(nodes_path, node_tags_path, ways_path, 
                                       way_nodes_path, way_tags_path)
    
    # Create a database connection
    conn = create_connection(db_path)

    # Create tables in SQL DB and import .csv files
    table_names = {}
    for csv_file, sql_schema in sql_table_schemas.items():
        table_names[csv_file] = create_table(conn, sql_schema)
        import_csv(conn, csv_file, table_names[csv_file])
    
    conn.close()


if __name__ == '__main__':
    """Defines the required variables if the code is launched in stand-alone mode"""
    
    SQL_DB_PATH = 'LCG_map.db'
    
    NODES_PATH = 'nodes.csv'
    NODE_TAGS_PATH = 'nodes_tags.csv'
    WAYS_PATH = 'ways.csv'
    WAY_NODES_PATH = 'ways_nodes.csv'
    WAY_TAGS_PATH = 'ways_tags.csv'
    
    create_database(SQL_DB_PATH, NODES_PATH, NODE_TAGS_PATH, WAYS_PATH, 
                    WAY_NODES_PATH, WAY_TAGS_PATH)
