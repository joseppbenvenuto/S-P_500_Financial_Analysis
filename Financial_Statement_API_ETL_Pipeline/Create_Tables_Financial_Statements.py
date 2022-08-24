import psycopg2 as ps
from SQL_Queries_Financial_Statements import *

###########################################################################################################################################
# NEW CODE BLOCK - Create financialdb
###########################################################################################################################################

def create_database():
    """
    - Creates and connects to the edgardb
    - Returns the connection and cursor to financialdb
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

    # create financialdb database with UTF8 encoding
    cur.execute('DROP DATABASE IF EXISTS financialdb;')
    cur.execute("CREATE DATABASE financialdb WITH ENCODING 'utf8' TEMPLATE template0;")

    # close connection to default database
    conn.close()

    # connect to financialdb database
    conn = ps.connect('''
    
        host=localhost
        dbname=financialdb
        user=postgres
        password=iEchu133
        
    ''')

    cur = conn.cursor()

    return cur, conn


###########################################################################################################################################
# NEW CODE BLOCK - Create tables in financialdb
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
    Creates financial statement view
    """
    cur.execute(financial_statement_view_create)
    conn.commit()
    
###########################################################################################################################################
# NEW CODE BLOCK - Runs etl pipeline
###########################################################################################################################################

def main():
    """
    - Drops (if exists) and creates the financialdb database
    - Establishes connection with the financialdb database and gets cursor to it
    - Drops all the tables
    - Creates all tables needed and financial statement view
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
        
        # Create financial statement view
        create_view(
            cur = cur, 
            conn = conn
        )
        
        print('Tables have been created: companies, company_financials, financial_accounts, financial_statements, time, and financial_statement_view')
    
        cur.close()
        conn.close()

    except ps.Error as e:
        print('\n Error:')
        print(e)


if __name__ == "__main__":
    main()
