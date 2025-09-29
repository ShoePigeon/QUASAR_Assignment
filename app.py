import dash
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def load_data():
    # Load the dataset while ignoring the comment lines and blank lines
    df = pd.read_csv(
        'EEG and ECG data_02_raw.csv',
        comment='#',
        skip_blank_lines=True
    )
    # Drop the unwanted columns
    columns_to_drop = ['X3:', 'Trigger', 'Time_Offset', 'ADC_Status', 'ADC_Sequence', 'Event', 'Comments']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    # Rename ECG columns
    df = df.rename(columns={
        'X1:LEOG': 'Left ECG',
        'X2:REOG': 'Right ECG'
    })
    time_col = ['Time']
    ecg_cols = ['Left ECG', 'Right ECG']
    
    # Get remaining columns (excluding Time and ECGs)
    other_cols = sorted([col for col in df.columns if col not in time_col + ecg_cols])

    # Final column order
    new_order = time_col + other_cols + ecg_cols
    df = df[new_order]

    return df


data = load_data()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

graph1_controls = dbc.Card([
        dbc.CardHeader("Channel Selection"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='channel-dropdown',
                        options=[
                            {'label': col, 'value': col}
                            for col in data.columns if col not in ['Time', 'CM']
                        ],
                        value=[data.columns[1]],
                        clearable=True,
                        multi=True
                    )
                ], width=6),

                dbc.Col([
                    dbc.Checklist(
                        options=[{"label": "Show Common Mode (CM)", "value": "CM"}],
                        value=["CM"],
                        id="cm-toggle",
                        switch=True
                    )
                ], width=4)
            ])
        ])
    ], className="mb-4")

graph1_graph = dbc.Card([
        dbc.CardHeader("Time Series Plot"),
        dbc.CardBody([
            dcc.Graph(id='time-series-graph')
        ])
    ])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("EEG and ECG Data Visualization"), className="my-4 text-center")
    ]),

    graph1_controls,
    graph1_graph
], fluid=True)



@app.callback(
    Output('time-series-graph', 'figure'),
    Input('channel-dropdown', 'value'),
    Input('cm-toggle', 'value')
)
def first_update_graph(selected_channels, cm_toggle):
    if not selected_channels and cm_toggle != ['CM']:
        fig = go.Figure()
        fig.update_layout(
            title='No channels selected',
            xaxis=dict(title='Time (seconds)'),
            yaxis=dict(title='Value')
        )
        return fig
    fig = go.Figure()

    ECG_Channels = ['Right ECG', 'Left ECG']  #ECG Channels
    selected_channels.sort(key= lambda x: (x in ECG_Channels, x))  # Sort to have ECG channels last
    

    for channel in selected_channels:
        if channel in ECG_Channels:
            # alias = change_name(channel)
            fig.add_trace(go.Scatter(
                x=data['Time'],
                y=data[channel],
                mode='lines',
                line=dict(width=1),
                name=channel,
                yaxis='y2'  # assign to secondary y-axis
            ))
        else:
            fig.add_trace(go.Scatter(
                x=data['Time'],
                y=data[channel],
                mode='lines',
                line=dict(width=1),
                name=channel
                # default yaxis = 'y'
            ))


    # Conditionally add CM if checkbox is checked
    if 'CM' in cm_toggle:
        fig.add_trace(go.Scatter(
            x=data['Time'],
            y=data['CM'],
            mode='lines',
            name='CM (Common Mode)',
            line=dict(width=2, dash='dash', color='gray')
        ))


    # Update layout to add secondary y-axis on right side
    fig.update_layout(
        title='Channels v Time',
        title_x=0.5,
        xaxis=dict(title='Time (seconds)'),
        yaxis=dict(
            title='EEG Channels (µV)',
            side='left'
        ),
        yaxis2=dict(
            title='ECG Channels (mV)',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend=dict(x=0, y=1)
    )

    return fig
    


if __name__ == "__main__":
    app.run(debug=True)