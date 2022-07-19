from dash import html, dash_table
import pandas as pd


df = [{'Account': 'Revenue', '2021': 200, '2022': 300}, 
      {'Account': 'Operating Income', '2021': 100, '2022': 200}, 
      {'Account': 'Net Income', '2021': 50, '2022': 150}]

df = pd.DataFrame(df)


layout = html.Div([
    
    # Instructions
    html.Div([

        html.H2(
            'Income Statement',
            style = {
                'padding':10,
                'padding-top':10,
                'margin-top':50,
                'font-family':'Arial, Helvetica, sans-serif',
                # 'background':'#00008B',
                # 'color':'#FFFFFF',
                'textAlign':'left'
            }
        ),
        
        html.Div([
            dash_table.DataTable(
                data = df.to_dict('records'),
                columns = [{'id': c, 'name': c} for c in df.columns],
                style_cell_conditional = [
                    {
                        'if': {'column_id': c},
                        'textAlign': 'left'
                    } for c in ['Account']
                ],
                style_cell = {'font-family':'Arial, Helvetica, sans-serif'},
                style_as_list_view = True,
                style_header = {
                    'font-family':'Arial, Helvetica, sans-serif',
                    'font-size': 18,
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                }
            )
        ], 
        
        style = {
            'font-family':'Arial, Helvetica, sans-serif',
            'padding-top': 10,
            'padding-left': 10,
            'padding-right': 15,
            'padding-bottom': 10,
        })
    ]),
])