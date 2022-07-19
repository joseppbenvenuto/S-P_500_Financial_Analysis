import psycopg2 as ps
from SQL_Queries_EDGAR import *

###########################################################################################################################################
# NEW CODE BLOCK - Create nhldb
###########################################################################################################################################

def create_database():
    """
    - Creates and connects to the nhldb
    - Returns the connection and cursor to nhldb
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

    # create MailChimpdb database with UTF8 encoding
    cur.execute('DROP DATABASE IF EXISTS edgardb;')
    cur.execute("CREATE DATABASE edgardb WITH ENCODING 'utf8' TEMPLATE template0;")

    # close connection to default database
    conn.close()

    # connect to edgardb database
    conn = ps.connect('''
    
        host=localhost
        dbname=edgardb
        user=postgres
        password=iEchu133
        
    ''')

    cur = conn.cursor()

    return cur, conn


###########################################################################################################################################
# NEW CODE BLOCK - Create tables in nhldb
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
    Creates edgar view
    """
    cur.execute(edgard_view_create)
    conn.commit()
    
   ###########################################################################################################################################
# NEW CODE BLOCK - Team names and IDs from NHL API
###########################################################################################################################################

def main():
    """
    - Drops (if exists) and creates the edgardb database
    - Establishes connection with the edgardb database and gets cursor to it
    - Drops all the tables
    - Creates all tables needed and edgar sview
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
        
        # Create edgar view 
        create_view(
            cur = cur, 
            conn = conn
        )
        
        print('Tables have been created: companies, company_financials, and edgard_view')
    
        cur.close()
        conn.close()

    except ps.Error as e:
        print('\n Error:')
        print(e)


if __name__ == "__main__":
    main()
