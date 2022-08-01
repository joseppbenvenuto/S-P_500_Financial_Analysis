###########################################################################################################################################
# NEW CODE BLOCK - Drop all tables
###########################################################################################################################################

# DROP TABLES
companies_table_drop = "DROP TABLE IF EXISTS companies;"
financial_acc_table_drop = "DROP TABLE IF EXISTS financial_accounts;"
financial_acc_descriptions_table_drop = "DROP TABLE IF EXISTS financial_accounts_descriptions;"
company_financials_table_drop = "DROP TABLE IF EXISTS company_financials;"

###########################################################################################################################################
# NEW CODE BLOCK - Delete rows
###########################################################################################################################################

companies_table_drop_rows = "DELETE FROM companies;"
financial_acc_table_drop_rows = "DELETE FROM financial_accounts;"
financial_acc_descriptions_table_drop_rows = "DELETE FROM financial_accounts_descriptions;"
company_financials_table_drop_rows = "DELETE FROM company_financials;"


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

financial_acc_table_create = ("""

    CREATE TABLE IF NOT EXISTS financial_accounts(
        id SERIAL NOT NULL PRIMARY KEY,
        financial_acc_id int NOT NULL,
        field varchar NOT NULL
    );
    
""")

financial_acc_descriptions_table_create = ("""

    CREATE TABLE IF NOT EXISTS financial_accounts_descriptions(
        id SERIAL NOT NULL PRIMARY KEY,
        financial_acc_descriptions_id int NOT NULL,
        description varchar NOT NULL
    );
    
""")

# FACT TABLE
company_financials_table_create = ("""

    CREATE TABLE IF NOT EXISTS company_financials(
        company_financials_id SERIAL NOT NULL PRIMARY KEY,
        cik int NOT NULL,
        financial_acc_id int NOT NULL,
        financial_acc_descriptions_id int NOT NULL,
        "end" varchar,
        val float NOT NULL,
        accn varchar,
        fy varchar,
        fp varchar,
        form varchar,
        filed varchar,
        start varchar,
        frame int NOT NULL
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

# financial_acc_table_col_num = 2
# financial_acc_table_variables = '%s' + (',%s' * (financial_acc_table_col_num - 1))
# financial_acc_table_insert = ("""

#     INSERT INTO financial_accounts(
#         financial_acc_id,
#         field
#     )
#     VALUES (""" + financial_acc_table_variables + """)
#     ON CONFLICT (financial_acc_id)
#         DO UPDATE
#             SET
#                 field = EXCLUDED.field;
                
# """)

# financial_acc_descriptions_table_col_num = 2
# financial_acc_descriptions_table_variables = '%s' + (',%s' * (financial_acc_descriptions_table_col_num - 1))
# financial_acc_descriptions_table_insert = ("""

#     INSERT INTO financial_accounts_descriptions(
#         financial_acc_descriptions_id,
#         description
#     )
#     VALUES (""" + financial_acc_descriptions_table_variables + """)
#     ON CONFLICT (financial_acc_descriptions_id)
#         DO UPDATE
#             SET
#                 description = EXCLUDED.description;
                
# """)


###########################################################################################################################################
# NEW CODE BLOCK - Create View
###########################################################################################################################################

# Create edgar start view
edgard_view_pre_create = ('''

    CREATE VIEW edgar_view_pre AS
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
           cf.frame,
           cf.financial_acc_id,
           fa.field,
           cf.financial_acc_descriptions_id,
           fad.description
    FROM company_financials AS cf LEFT JOIN companies AS co
    ON cf.cik = co.cik
    LEFT JOIN financial_accounts AS fa
    ON cf.company_financials_id = fa.id
    LEFT JOIN financial_accounts_descriptions AS fad
    ON cf.company_financials_id = fad.id
    ORDER BY cik ASC;
    
''')

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
           cf.frame,
           cf.financial_acc_id,
           fa.field,
           cf.financial_acc_descriptions_id,
           fad.description
    FROM company_financials AS cf LEFT JOIN companies AS co
    ON cf.cik = co.cik
    LEFT JOIN financial_accounts AS fa
    ON cf.financial_acc_id = fa.financial_acc_id
    LEFT JOIN financial_accounts_descriptions AS fad
    ON cf.financial_acc_descriptions_id = fad.financial_acc_descriptions_id
    ORDER BY cik ASC;
    
''')


###########################################################################################################################################
# NEW CODE BLOCK - Query lists
###########################################################################################################################################

# QUERY LISTS
create_table_queries = [
    companies_table_create, 
    financial_acc_table_create,
    financial_acc_descriptions_table_create,
    company_financials_table_create
]

drop_table_queries = [
    companies_table_drop, 
    financial_acc_table_drop,
    financial_acc_descriptions_table_drop,
    company_financials_table_drop
]
