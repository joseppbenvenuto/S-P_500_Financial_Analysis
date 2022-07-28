###########################################################################################################################################
# NEW CODE BLOCK - Drop all tables
###########################################################################################################################################

# DROP TABLES
balance_sheet_table_drop = "DROP TABLE IF EXISTS balance_sheet;"
income_statement_table_drop = "DROP TABLE IF EXISTS income_statement;"
cash_flow_statement_table_drop = "DROP TABLE IF EXISTS cash_flow;"


###########################################################################################################################################
# NEW CODE BLOCK - Create all tables
###########################################################################################################################################

# CREATE TABLES
# DIMENSION TABLES
balance_sheet_table_create = ("""

    CREATE TABLE IF NOT EXISTS balance_sheet(
        balance_sheet_id SERIAL NOT NULL PRIMARY KEY,
        financial_statement_type varchar NOT NULL,
        financial_accounts varchar NOT NULL,
        date varchar NOT NULL,
        financial_values varchar NOT NULL,
        ticker varchar NOT NULL
        
    );
    
""")

income_statement_table_create = ("""

    CREATE TABLE IF NOT EXISTS income_statement(
        income_statement_id SERIAL NOT NULL PRIMARY KEY,
        financial_statement_type varchar NOT NULL,
        financial_accounts varchar NOT NULL,
        date varchar NOT NULL,
        financial_values varchar NOT NULL,
        ticker varchar NOT NULL
        
    );
    
""")

cash_flow_table_create = ("""

    CREATE TABLE IF NOT EXISTS cash_flow_statement(
        cash_flow_id SERIAL NOT NULL PRIMARY KEY,
        financial_statement_type varchar NOT NULL,
        financial_accounts varchar NOT NULL,
        date varchar NOT NULL,
        financial_values varchar NOT NULL,
        ticker varchar NOT NULL
        
    );
    
""")


###########################################################################################################################################
# NEW CODE BLOCK - Create View
###########################################################################################################################################

# Create yahoo view
yahoo_view_create = ('''

    CREATE VIEW yahoo_view AS
    SELECT financial_statement_type, financial_accounts, date, financial_values, ticker
    FROM balance_sheet
    UNION
    SELECT financial_statement_type, financial_accounts, date, financial_values, ticker
    FROM cash_flow_statement
    UNION
    SELECT financial_statement_type, financial_accounts, date, financial_values, ticker
    FROM income_statement;
    
''')


###########################################################################################################################################
# NEW CODE BLOCK - Query lists
###########################################################################################################################################

# QUERY LISTS
create_table_queries = [
    balance_sheet_table_create, 
    income_statement_table_create,
    cash_flow_table_create
]

drop_table_queries = [
    balance_sheet_table_drop, 
    income_statement_table_drop, 
    cash_flow_statement_table_drop
]
