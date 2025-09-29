import dash
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html
import plotly.express as px
import pandas as pd

def load_data():
    # Load the dataset while ignoring the comment lines and blank lines
    df = pd.read_csv(
        'EEG and ECG data_02_raw.csv',
        comment = '#',
        skip_blank_lines=True
        )
    # Drop the unwanted columns (if they exist in the file)
    columns_to_drop = ['X3:', 'Trigger', 'Time_Offset', 'ADC_Status', 'ADC_Sequence', 'Event', 'Comments']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
    return df


data = load_data()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("EEG and ECG Data Visualization"), className="mb-2 text-center")
    ]),
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='channel-dropdown',
            options=[{'label': col, 'value': col} for col in data.columns if col != 'Time'],
            value=data.columns[1],
            clearable=False
        ), width=4)
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='time-series-graph'), width=12)
    ])
], fluid=True)


@app.callback(
    Output('time-series-graph', 'figure'),
    Input('channel-dropdown', 'value')
)
def update_graph(selected_channel):
    fig = px.line(data, x='Time', y=selected_channel, title=f'Time Series of {selected_channel}')
    fig.update_layout(xaxis_title='Time', yaxis_title=selected_channel)
    return fig






if __name__ == "__main__":
    app.run(debug=True)