import psycopg2 as ps
from SQL_Queries_Yahoo_Finance import *

###########################################################################################################################################
# NEW CODE BLOCK - Create yahoodb
###########################################################################################################################################

def create_database():
    """
    - Creates and connects to the yahoodb
    - Returns the connection and cursor to yahoodb
    """

    # connect to default database port: 5432
    conn = ps.connect('''
    
        host=localhost
        dbname=postgres
        user=postgres
        password=iEchu133
           
    ''')

    conn.set_session(autocommit = True)
    cur = conn.cursor()

    # create yahoodb database with UTF8 encoding
    cur.execute('DROP DATABASE IF EXISTS yahoodb;')
    cur.execute("CREATE DATABASE yahoodb WITH ENCODING 'utf8' TEMPLATE template0;")

    # close connection to default database
    conn.close()

    # connect to edgardb database
    conn = ps.connect('''
    
        host=localhost
        dbname=yahoodb
        user=postgres
        password=iEchu133
        
    ''')

    cur = conn.cursor()

    return cur, conn


###########################################################################################################################################
# NEW CODE BLOCK - Create tables in yahoodb
###########################################################################################################################################


def drop_tables(cur, conn):
    """
    Drops each table using the queries in `drop_table_queries` list
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    Creates each table using the queries in `create_table_queries` list
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()
        
        
def create_view(cur, conn):
    """
    Creates yahoo view
    """
    cur.execute(yahoo_view_create)
    conn.commit()
    
   ###########################################################################################################################################
# NEW CODE BLOCK - Runs etl pipeline
###########################################################################################################################################

def main():
    """
    - Drops (if exists) and creates the yahoodb database
    - Establishes connection with the yahoo database and gets cursor to it
    - Drops all the tables
    - Creates all tables needed and yahoo view
    - Closes the connection
    """

    try:
        cur, conn = create_database()
        
        # Drop tables
        drop_tables(
            cur = cur, 
            conn = conn
        )
        
        # Create tables
        create_tables(
            cur = cur, 
            conn = conn
        )
        
        # Create yahoo view 
        create_view(
            cur = cur, 
            conn = conn
        )
        
        print('Tables have been created: balance_sheet, income_statement, cash_flow_statement, and yahoo_view')
    
        cur.close()
        conn.close()

    except ps.Error as e:
        print('\n Error:')
        print(e)


if __name__ == "__main__":
    main()
