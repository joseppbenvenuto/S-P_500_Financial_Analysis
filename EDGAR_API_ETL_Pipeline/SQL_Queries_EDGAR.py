###########################################################################################################################################
# NEW CODE BLOCK - Drop all tables
###########################################################################################################################################

# DROP TABLES
companies_table_drop = "DROP TABLE IF EXISTS companies;"
# financial_accounts_table_drop = "DROP TABLE IF EXISTS financial_accounts;"
company_financials_table_drop = "DROP TABLE IF EXISTS company_financials;"


###########################################################################################################################################
# NEW CODE BLOCK - Drop all rows
###########################################################################################################################################

# # DROPS ALL ROWS FROM EXISTING TABLE
# company_financials_table_drop_rows = "DELETE FROM company_financials;"


###########################################################################################################################################
# NEW CODE BLOCK - Create all tables
###########################################################################################################################################

# CREATE TABLES
# DIMENSION TABLES
companies_table_create = ("""

    CREATE TABLE IF NOT EXISTS companies(
        cik int NOT NULL PRIMARY KEY,
        company varchar NOT NULL,
        ticker varchar
        
    );
    
""")

# financial_accounts_table_create = ("""

#     CREATE TABLE IF NOT EXISTS financial_accounts(
#         financial_accounts_id varchar NOT NULL PRIMARY KEY,
#         field varchar NOT NULL,
#         description varchar
#     );
    
# """)

# FACT TABLE
company_financials_table_create = ("""

    CREATE TABLE IF NOT EXISTS company_financials(
        company_financials_id SERIAL NOT NULL PRIMARY KEY,
        cik int NOT NULL,
        "end" varchar,
        val float NOT NULL,
        accn varchar,
        fy varchar,
        fp varchar,
        form varchar,
        filed varchar,
        start varchar,
        field varchar NOT NULL,
        description varchar
    );
    
""")


###########################################################################################################################################
# NEW CODE BLOCK - Insert records
###########################################################################################################################################

# INSERT RECORDS
companies_table_col_num = 3
companies_table_variables = '%s' + (',%s' * (companies_table_col_num - 1))
companies_table_insert = ("""

    INSERT INTO companies(
        cik,
        company,
        ticker
    )
    VALUES (""" + companies_table_variables + """)
    ON CONFLICT (cik)
        DO UPDATE
            SET
                company = EXCLUDED.company,
                ticker = EXCLUDED.ticker;
                
""")

# financial_accounts_table_col_num = 3
# financial_accounts_table_variables = '%s' + (',%s' * (financial_accounts_table_col_num - 1))
# financial_accounts_table_insert = ("""

#     INSERT INTO financial_accounts(
#         financial_accounts_id,
#         field,
#         description
#     )
#     VALUES (""" + financial_accounts_table_variables + """)
#     ON CONFLICT (financial_accounts_id)
#         DO UPDATE
#             SET
#                 field = EXCLUDED.field,
#                 description = EXCLUDED.description;
                
# """)


###########################################################################################################################################
# NEW CODE BLOCK - Create View
###########################################################################################################################################

# Create edgar view
edgard_view_create = ('''

    CREATE VIEW edgar_view AS
    SELECT co.cik,
           co.company,
           co.ticker,
           cf.end,
           cf.accn,
           cf.fp,
           cf.form,
           cf.filed,
           cf.start,
           cf.val,
           cf.fy,
           cf.field,
           cf.description
    FROM company_financials AS cf LEFT JOIN companies AS co
    ON cf.cik = co.cik
    ORDER BY cik ASC;
    
''')


###########################################################################################################################################
# NEW CODE BLOCK - Query lists
###########################################################################################################################################

# QUERY LISTS
create_table_queries = [
    companies_table_create, 
#     financial_accounts_table_create,
    company_financials_table_create
]

drop_table_queries = [
    companies_table_drop, 
#     financial_accounts_table_drop, 
    company_financials_table_drop
]
