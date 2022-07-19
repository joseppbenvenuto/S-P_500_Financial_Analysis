import pandas as pd
import psycopg2 as ps

def edgar_view_csv():
    # Connect to database
    try:
        conn = ps.connect('''

            host=localhost
            dbname=edgardb
            user=postgres
            password=iEchu133

        ''')

        cur = conn.cursor()

        print('Successfully connected to edgardb')

    except ps.Error as e:
        print('\n Database Error:')
        print(e)

    try:
        # Query view from edgardb
        query = '''

            SELECT *
            FROM edgar_view;

        '''

        cur.execute(query)
        edgar_df = cur.fetchall()

        edgar_columns = [
            'cik',
            'company',
            'ticker',
            'end',
            'accn',
            'fp',
            'form',
            'filed',
            'start',
            'val',
            'fy',
            'field',
            'description'
        ]

        # Convert view to pandas data frame
        edgar_df = pd.DataFrame(edgar_df, columns = edgar_columns)

        # Filter out data without years
        edgar_df = edgar_df.loc[
            (edgar_df['fy'] != '') & 
            (edgar_df['ticker'] != 'NaN')
        ]

        edgar_df.to_csv('US_GAAP_ACC_Numbers.csv', index = False)
        
        print('US_GAAP_ACC_Numbers.csv created')
        
    except Exception as e:
        print('CSV error:')
        print(e)
    
    
if __name__ == '__main__':
    edgar_view_csv()