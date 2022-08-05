###########################################################################################################################################
# NEW CODE BLOCK - Drop all tables
###########################################################################################################################################

# DROP TABLES
companies_table_drop = "DROP TABLE IF EXISTS companies;"
financial_acc_table_drop = "DROP TABLE IF EXISTS financial_accounts;"
financial_statement_table_drop = "DROP TABLE IF EXISTS financial_statements;"
company_financials_table_drop = "DROP TABLE IF EXISTS company_financials;"
time_table_drop = "DROP TABLE IF EXISTS time;"

###########################################################################################################################################
# NEW CODE BLOCK - Delete rows
###########################################################################################################################################

companies_table_drop_rows = "DELETE FROM companies;"
financial_acc_table_drop_rows = "DELETE FROM financial_accounts;"
financial_statement_table_drop_rows = "DELETE FROM financial_statements;"
company_financials_table_drop_rows = "DELETE FROM company_financials;"
time_table_drop_rows = "DELETE FROM time;"

###########################################################################################################################################
# NEW CODE BLOCK - Create all tables
###########################################################################################################################################

# CREATE TABLES
# DIMENSION TABLES
companies_table_create = ("""

    CREATE TABLE IF NOT EXISTS companies(
        company_id int NOT NULL PRIMARY KEY,
        cik int NOT NULL,
        company varchar NOT NULL,
        ticker varchar
    );
    
""")

financial_acc_table_create = ("""

    CREATE TABLE IF NOT EXISTS financial_accounts(
        financial_accounts_id int NOT NULL PRIMARY KEY,
        financial_accounts varchar NOT NULL
    );
    
""")

financial_statement_table_create = ("""

    CREATE TABLE IF NOT EXISTS financial_statements(
        financial_statement_id int NOT NULL PRIMARY KEY,
        financial_statement varchar NOT NULL
    );
    
""")

time_table_create = ("""

    CREATE TABLE IF NOT EXISTS time(
        time_id int NOT NULL PRIMARY KEY,
        "date" date NOT NULL,
        filling_date date NOT NULL,
        accepted_date timestamp NOT NULL,
        calendar_year int NOT NULL
    );
    
""")

# FACT TABLE
company_financials_table_create = ("""

    CREATE TABLE IF NOT EXISTS company_financials(
        company_financials_id SERIAL NOT NULL PRIMARY KEY,
        financial_values bigint NOT NULL,
        company_id int NOT NULL,
        financial_accounts_id int NOT NULL,
        financial_statement_id int NOT NULL,
        time_id int NOT NULL
    );
    
""")


###########################################################################################################################################
# NEW CODE BLOCK - Create View
###########################################################################################################################################

# Create financial_statement_view
financial_statement_view_create = ('''

    CREATE VIEW financial_statement_view AS
    SELECT co.cik,
           co.company,
           co.ticker,
           fa.financial_accounts,
           fs.financial_statement,
           ti.date,
           ti.filling_date,
           ti.accepted_date,
           ti.calendar_year,
           cf.financial_values
    FROM company_financials AS cf LEFT JOIN financial_statements AS fs
    ON cf.financial_statement_id = fs.financial_statement_id
    LEFT JOIN companies AS co
    ON cf.company_id = co.company_id
    LEFT JOIN financial_accounts AS fa
    ON cf.financial_accounts_id = fa.financial_accounts_id
    LEFT JOIN time AS ti
    ON cf.time_id = ti.time_id;
    
''')


###########################################################################################################################################
# NEW CODE BLOCK - Query lists
###########################################################################################################################################

# QUERY LISTS
create_table_queries = [
    companies_table_create, 
    financial_acc_table_create,
    financial_statement_table_create,
    company_financials_table_create,
    time_table_create
]

drop_table_queries = [
    companies_table_drop, 
    financial_acc_table_drop,
    financial_statement_table_drop,
    company_financials_table_drop,
    time_table_drop
]
