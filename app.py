from __future__ import division

import json
import math

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

# Read in data.
data_file = 'data.csv'
raw_data = pd.read_csv('data.csv')

# Format datetime and extract year and month separately.
raw_data['Date of Contact'] = pd.to_datetime(raw_data['Date of Contact'], format='%Y-%m-%d')
raw_data['month'] = raw_data['Date of Contact'].dt.month
raw_data['year'] = raw_data['Date of Contact'].dt.year

# Instantiate a Dash object.
app = dash.Dash()
server = app.server

# Main Dash layout.
app.layout = html.Div(children=[

    # Title
    html.H1(children='Historical CRM Explorer',
            className='twelve columns',
            style={'text-align': 'center'}),

    # Hor Rule


    # Subtitle
    html.Div([
        html.Div([
            html.P('This app will allow you to explore historical client '
                      'contact data for all historical months, or months aggregated '
                      'across all available years.  Data may be filtered by Customer '
                      'Manager, or by individual Client.')],
                 style={'margin': 'auto', 'width': '90%'},
                 )
    ], className="row"),

    html.Hr(),
    
    # Filters
    html.Div([

        # Left Column
        html.Div([

            # Dropdown 1 - Team Member
            html.Div([
                html.Label('Choose an Account Manager:'),
                dcc.Dropdown(
                    id='account-manager',
                    options=[{'label': '-All Managers', 'value': 'All Managers'}] + \
                            [{'label': x, 'value': x} for x in sorted(raw_data['Account manager'].unique())],
                    value='All Managers'
                ),
            ], style={'margin-bottom': '10'}),

            # Dropdown 2 - Client
            html.Div([
                html.Label('Choose a Client:'),
                dcc.Dropdown(
                    id='client',
                    options=[{'label': '-All Clients', 'value': 'All Clients'}] + \
                            [{'label': x, 'value': x} for x in sorted(raw_data['Client Name'].unique())],
                    value='All Clients'
                )
            ])
        ], className="six columns"),

        # Right Columns
        html.Div([

            # Radio Button 1 - Time View
            html.Div([
                html.Label('Choose a Monthly View:'),
                dcc.RadioItems(
                    id='time-view',
                    options=[
                        {'label': 'All Historical Months', 'value': 'allhm'},
                        {'label': 'Months Aggregated Across Years', 'value': 'agghm'}
                    ],
                    value='allhm'
                )
            ], style={'margin-bottom': '10'}),

            # Radio Button 2 - Reporting Statistic
            html.Div([
                html.Label('Choose a Reporting Statistic:'),
                dcc.RadioItems(
                    id='reporting-statistic',
                    options=[
                        {'label': 'Total Contacts Made', 'value': 'tc'},
                        {'label': 'Unique Clients Contacted', 'value': 'ucc'},
                        {'label': 'Percentage of All Clients Contacted', 'value': 'pacc'}
                    ],
                    value='tc'
                )
            ])
        ], className="six columns")

    ], className="row", style={'margin': '20'}),


    html.Hr(),

    html.Div([

        html.Div([
            # Main Bar Chart.
            dcc.Graph(
                id='main-graph')],
            className="twelve columns"
        ),

        # Contact List.
        html.Div(id="table",
                 className="four columns",
                 style={"font-size": "1em"})
    ], className="row", style={'height':'200px'} )

])


# Callback 1 - User inputs.
@app.callback(
    dash.dependencies.Output('main-graph', 'figure'),
    [dash.dependencies.Input('account-manager', 'value'),
     dash.dependencies.Input('client', 'value'),
     dash.dependencies.Input('time-view', 'value'),
     dash.dependencies.Input('reporting-statistic', 'value')])
def update_main_graph(selected_account_manager, selected_client, selected_time_view, selected_reporting_statistic):

    # New view.
    data = raw_data

    # Time view.
    if selected_time_view == "allhm":
        groups = ['year', 'month']
    elif selected_time_view == "agghm":
        groups = ['month']

    # Subset Account Manager.
    if selected_account_manager != "All Managers":
        data = data[data['Account manager'] == selected_account_manager]

    # Subset Client.
    if selected_client != "All Clients":
        data = data[data['Client Name'] == selected_client]

    # Reporting Statistic.
    if selected_reporting_statistic == "tc":
        results = data.groupby(groups)['Client Name'].count().reset_index()
        y = results['Client Name']
    elif selected_reporting_statistic == "ucc":
        results = data.groupby(groups)['Client Name'].nunique().reset_index()
        y = results['Client Name']
    elif selected_reporting_statistic == "pacc":
        results = data.groupby(groups)['Client Name'].nunique().reset_index()
        y = results['Client Name'] / raw_data['Client Name'].nunique()

    # X values as strings.
    look_up = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul',
               8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    results['month'] = results['month'].apply(lambda x: look_up[x])

    if selected_time_view == "allhm":
        X = results[groups[1]].astype(str) + ", " + results[groups[0]].astype(str)
    else:
        X = results[groups[0]].astype(str)
        # Group by month and perform count of unique.
        #counts = data.groupby(['year', 'month'])['Client Name'].nunique().reset_index()

    return {
            'data': [go.Bar(x=X,
                            y=y,
                            text=y.astype(str))],
            'layout': go.Layout(xaxis={'type': 'category'},
                                margin={'l': '30',
                                        'r': '10',
                                        't': '10',
                                        'b': '80'}),
            }

"""
# Callback 2 - Chart Interactivity.
@app.callback(
    dash.dependencies.Output('table', 'children'),
    [dash.dependencies.Input('main-graph', 'clickData'),
     dash.dependencies.Input('account-manager', 'value'),
     dash.dependencies.Input('client', 'value'),
     dash.dependencies.Input('time-view', 'value')])
def update_table(clickData, selected_account_manager, selected_client, selected_time_view):

    data = raw_data
    clients = sorted(raw_data['Client Name'].unique())

    look_up = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7,
               'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

    # Time view.
    if selected_time_view == "allhm":
        clickMonth = clickData['points'][0]['x'].split(',')[0]
        clickYear = clickData['points'][0]['x'].split(',')[1]
        data = data[data['year'] == int(clickYear)]
        data = data[data['month'] == look_up[clickMonth]]
    elif selected_time_view == "agghm":
        clickMonth = clickData['points'][0]['x'].split(',')[0]
        clickYear = None
        data = data[data['month'] == look_up[clickMonth]]

    # Subset Account Manager.
    if selected_account_manager != "All Managers":
        data = data[data['Account manager'] == selected_account_manager]

    # Subset Client.
    if selected_client != "All Clients":
        data = data[data['Client Name'] == selected_client]

    # Group by client and count total contacts.
    results = data.groupby(['Client Name'])['Client Name'].count()

    # Build results.
    y = []
    for client in clients:
        if client in results:
            y.append(results[client])
        else:
            y.append(0)


    return [
        html.Table(
            [html.Tr([html.Th(col) for col in ['Client Name', 'Number of Contacts']])] +
            [html.Tr( [html.Td(clients[i]), html.Td(y[i])] ) for i in range(len(clients)) ],
            style={'overflow-y': 'scroll'}
        )
    ]



    html.Div([

        html.Table(
            # Header
            [html.Tr([html.Th(col) for col in ['Client Name', 'Date of Contact']])] +

            # Body
            [html.Tr([
                html.Td(raw_data.iloc[i][col]) for col in ['Client Name', 'Date of Contact']
            ]) for i in range(int(math.ceil(len(raw_data['Client Name'].unique())/2)),
                              len(raw_data['Client Name'].unique()))]
        )
    ], style={'display': 'inline-block', 'width': '49%', 'vertical-align': 'top'})

"""


# Style Sheet.
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

# Main.
if __name__ == '__main__':
    app.run_server(debug=True)