from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Connect to main app.py file
from App import app
from App import server

# Connect to your app pages
from Apps import Main_Page, Balance_Sheet, Income_Statement, Cash_Flow_Statement, Guru_Page, Instructions


app.layout = html.Div([

    # Header by company
    html.Div([

        html.H2(
            'Financial Trends & Accounting for US Companies',
            id = 'header',
            style = {
                'padding':10,
                'margin':0,
                'font-family':'Arial, Helvetica, sans-serif',
                'background':'#00008B',
                'color':'#FFFFFF',
                'textAlign':'center'
            }
        )
    ]),

    dcc.Location(
        id = 'url', 
        refresh = False
    ),

    html.Div([

        dcc.Link(

            dbc.Button(
                'Click for Financial Visulization', 
                style = {
                    'font-family':'Arial, Helvetica, sans-serif', 
                    'margin-left':'450px', 
                    'margin-top':'18px', 
                    'margin-bottom':'5px'
                }
            ),
            href = '/apps/Main_Page', 
            refresh = False
        ),
        
        # dcc.Link(
            
        #     dbc.Button(
        #         'Click for Balance Sheet',
        #         style = {
        #             'font-family':'Arial, Helvetica, sans-serif', 
        #             'margin-left':'15px', 
        #             'margin-top':'18px', 
        #             'margin-bottom':'5px'
        #         }
        #     ), 
            
        #     href = '/apps/Balance_Sheet', 
        #     refresh = False
        # ),
        
        # dcc.Link(
            
        #     dbc.Button(
        #         'Click for Income Statement',
        #         style = {
        #             'font-family':'Arial, Helvetica, sans-serif', 
        #             'margin-left':'15px', 
        #             'margin-top':'18px', 
        #             'margin-bottom':'5px'
        #         }
        #     ), 
            
        #     href = '/apps/Income_Statement', 
        #     refresh = False
        # ),
        
        # dcc.Link(
            
        #     dbc.Button(
        #         'Click for Cash-Flow Statement',
        #         style = {
        #             'font-family':'Arial, Helvetica, sans-serif', 
        #             'margin-left':'15px', 
        #             'margin-top':'18px', 
        #             'margin-bottom':'5px'
        #         }
        #     ), 
            
        #     href = '/apps/Cash_Flow_Statement', 
        #     refresh = False
        # ),
        
        dcc.Link(
            
            dbc.Button(
                'Click for Guru Educational Videos',
                style = {
                    'font-family':'Arial, Helvetica, sans-serif', 
                    'margin-left':'15px', 
                    'margin-top':'18px', 
                    'margin-bottom':'5px'
                }
            ), 
            
            href = '/apps/Guru_Page', 
            refresh = False
        ),
        
        dcc.Link(

            dbc.Button(
                'Click for Application Instructions',
                style = {
                    'font-family':'Arial, Helvetica, sans-serif', 
                    'margin-left':'15px', 
                    'margin-top':'18px', 
                    'margin-bottom':'5px'
                }
            ), 
            href = '/apps/Instructions', 
            refresh = False
        ),
    
    ], className = 'd-grid gap-2 d-md-block'),
    
    html.Div(
        id = 'page-content', 
        children = []
        )
])


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def display_page(pathname):
    if pathname == '/apps/Main_Page':
        return Main_Page.layout
    
    # if pathname == '/apps/Balance_Sheet':
    #     return Balance_Sheet.layout
    
    # if pathname == '/apps/Income_Statement':
    #     return Income_Statement.layout

    # if pathname == '/apps/Cash_Flow_Statement':
    #     return Cash_Flow_Statement.layout
    
    if pathname == '/apps/Guru_Page':
        return Guru_Page.layout

    if pathname == '/apps/Instructions':
        return Instructions.layout
    
    else:
        return Main_Page.layout


if __name__ == '__main__':
    app.run_server(debug=False)
