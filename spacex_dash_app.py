# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    # dcc.Dropdown(id='site-dropdown',...)
    dcc.Dropdown(
        id='site-dropdown',  # ID attribute
        options=[  # List of option objects
            {'label': 'All Sites', 'value': 'ALL'},  # Default option for all sites
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
        ],
        value='ALL',  # Default value (all sites selected)
        placeholder='Select a Launch Site here',  # Placeholder text
        searchable=True  # Enable keyword search for launch sites
    ),
    html.Br(),
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.Br(),  # Move the line break to after the pie chart div

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    # dcc.RangeSlider(id='payload-slider',...)
    dcc.RangeSlider(
        id='payload-slider',
        min=0,  # Minimum payload value (0 Kg)
        max=10000,  # Maximum payload value (10,000 Kg)
        step=1000,  # Slider interval (1,000 Kg)
        marks={i: str(i) for i in range(0, 10001, 1000)},  # Marks for every 1,000 Kg interval
        value=[min_payload, max_payload]  # Default selected range (min_payload to max_payload)
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
) 
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site != 'ALL':
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    
    success_counts = filtered_df[filtered_df['class'] == 1]['class'].count()
    failed_counts = filtered_df[filtered_df['class'] == 0]['class'].count()
    
    labels = ['Success', 'Failed']
    values = [success_counts, failed_counts]
    
    fig = px.pie(
        values=values,
        names=labels,
        title='Success vs. Failed Launches'
    )
    
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id="payload-slider", component_property="value")]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

    min_payload, max_payload = payload_range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= min_payload) & 
                              (filtered_df['Payload Mass (kg)'] <= max_payload)]

    fig = px.scatter(filtered_df, 
                     x='Payload Mass (kg)', 
                     y='class', 
                     color='Booster Version Category',
                     title='Payload Success vs. Payload Mass',
                     labels={'class': 'Launch Outcome'},
                     hover_name='Booster Version')

    fig.update_layout(xaxis_title='Payload Mass (kg)', yaxis_title='Launch Outcome')

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()