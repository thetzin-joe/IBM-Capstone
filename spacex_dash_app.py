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
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                html.Div(
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[
                                            {'label': 'All Sites', 'value': 'ALL'},
                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                        ],
                                        value = 'ALL',
                                        placeholder = 'Select a Launch Site here',
                                        searchable = True
                                    )
                                ),
                            
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.Div(
                                    dcc.RangeSlider(
                                        id='payload-slider',
                                        min = 0, max = 10000, step = 1000,
                                        marks = {0:'0', 100:'100'},
                                        value = [0, 10000]
                                    )
                                ),


                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output


@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # Check if 'ALL' sites were selected
    if entered_site == 'ALL':
        # Filter dataframe for successful launches
        success_df = spacex_df[spacex_df['class'] == 1]
        
        # Group by 'Launch Site' and count successes
        site_counts = success_df['Launch Site'].value_counts().reset_index()
        site_counts.columns = ['Launch Site', 'Success Count']
        
        # Create pie chart for all sites
        fig = px.pie(site_counts, values='Success Count', names='Launch Site', 
                     title='Proportion of Successful Launches by Launch Site')
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Create pie chart showing success/failure counts for the selected site
        title = f'Total Successful Launches for site {entered_site}'
        fig = px.pie(filtered_df, names='class', title=title,
                     color='class',
                     color_discrete_map={1: 'green', 0: 'red'},
                     labels={'class': 'Launch Outcome'},
                     )  # Added a hole for a donut chart appearance

        # Update the layout for clearer presentation
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(legend_title_text='Launch Outcome')

    return fig



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter(site, payload_range):
    # Filter spacex_df for the selected payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    # Check if 'ALL' sites were selected or a specific launch site
    if site == 'ALL':
        # Use filtered DataFrame for all sites
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', 
                         color='Booster Version Category', 
                         title='Launch Outcomes by Payload Mass for All Sites',
                         labels={'class': 'Launch Outcome'},
                         hover_data=['Booster Version'])
    else:
        # Further filter for the selected site
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == site]
        fig = px.scatter(site_filtered_df, x='Payload Mass (kg)', y='class', 
                         color='Booster Version Category', 
                         title=f'Launch Outcomes by Payload Mass for {site}',
                         labels={'class': 'Launch Outcome'},
                         hover_data=['Booster Version'])

    # Update figure layout if needed
    fig.update_layout(xaxis_title='Payload Mass (kg)', yaxis_title='Launch Outcome', yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['Failure', 'Success']))

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8030)
