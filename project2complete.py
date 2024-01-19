import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly_express as px
import dash_bootstrap_components as dbc

airline_df = pd.read_csv("https://docs.google.com/spreadsheets/d/1fabcggUcyCiY2Dq0bWsFvwzIjTlG-QLmLSl-jWzFDtc/export?format=csv")

map_df = airline_df.groupby(['latitude', 'longitude', "Airport.Name","Airport.Code"]).agg({'Statistics.Flights.Total': 'mean'}).reset_index().round(0)
fig = px.scatter_mapbox(
    map_df,
    lat="latitude",
    lon="longitude",
    mapbox_style="carto-positron",
    color="Statistics.Flights.Total",
    size="Statistics.Flights.Total",
    zoom=2.25,
    hover_data=["Airport.Name","Airport.Code","Statistics.Flights.Total"],
    title="Atlanta has an average of ~34,000 flights",
    labels={"Statistics.Flights.Total":"Average Number of Flights", "Airport.Name":"Airport Name"}
)


app = Dash(__name__,external_stylesheets=[dbc.themes.MATERIA])
server = app.server
app.layout = html.Div(
    [
        html.H1("Airline Data (2003-2016)"),
        html.P("Welcome! Hover over a location on the map to see that Airport's data in the bar chart."),
        dbc.Row([
            dbc.Col(dcc.Graph(id="mapchart",figure=fig),width=7),
            dbc.Col(dcc.Graph(id="barchart"),width=5),
            ]
        ),
        
        dbc.Row([
            dbc.Col(dcc.Graph(id="linechart")), 
            dbc.Col(dcc.Graph(id="scatterchart")),
        ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        options=airline_df["Airport.Name"].sort_values().unique(),
                        value="Boston, MA: Logan International",
                        id="airport-dropdown"
                    ),width=6
                ),
                dbc.Col(
                    dcc.RadioItems(
                        options=airline_df["Time.Month Name"].unique(),
                        style={'columnCount': 2},
                        value="January",
                        id="radio-buttons",
                    ),width=6
                )
            ]
        ),
        html.Br(),
        html.Div(id='popup', style={'display': 'none'}),
        dbc.Row(
            [
                dbc.Col(
                    html.Button(
                        "Bubble Chart",
                        id="bubble-button",
                    ),
                ),
                dbc.Col(
                    html.Button(
                        "Box Plot",
                        id="box-button",
                    )
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="bubble"),
                    width=6
                ),
                dbc.Col(
                    dcc.Graph(id="box"),
                    width=6
                ),
            ]
        )
    ]
)

@app.callback(
    Output("linechart","figure"),
    Input("airport-dropdown","value")
)

def update_line(airport_name):
    df = airline_df[airline_df["Airport.Name"] == airport_name]
    plot_df = df.groupby("Time.Year",as_index=False).agg({"Statistics.Flights.Delayed":"mean"})
    fig = px.line(
    plot_df,
    x="Time.Year",
    y="Statistics.Flights.Delayed",
    title="2007 sees a peak in delays across all Airports",
    labels= {"Time.Year":"Year" ,'Statistics.Flights.Delayed' : 'Average Flights Delayed'},
    template="simple_white",
    color_discrete_sequence=["cornflowerblue"]
    
)   
    return fig

@app.callback(
    Output("scatterchart","figure"),
    Input("radio-buttons","value"),
)

def update_scatter(month):
    scatter_df = airline_df[airline_df["Time.Month Name"] == month]
    max_index = scatter_df['Statistics.Flights.Cancelled'].idxmax()
    fig = px.scatter(
        scatter_df,
        x="Statistics.Flights.Total",
        y="Statistics.Flights.Cancelled",
        title="Chicago O'Hare in January had ~3700 flights cancelled",
        labels={"Statistics.Flights.Total":"Total Flights","Statistics.Flights.Cancelled":"Flights Cancelled"},
        template="simple_white",
        hover_data="Airport.Name",
    )
    fig.update_traces(
        marker=dict(
            size=10,
            symbol=["x" if i == max_index else "circle" for i in scatter_df.index],
            color=["crimson" if i == max_index else "cornflowerblue" for i in scatter_df.index]
        )
    )


    return fig

@app.callback(
    Output("barchart","figure"),
    Input("mapchart","hoverData")
)

def update_bar(hover_data):
    if hover_data is not None:
        airport = hover_data['points'][0]['customdata'][1]
        title=f"Total flights each Month for {airport}"
        plot_df = airline_df[airline_df["Airport.Code"] == airport].groupby("Time.Month Name",as_index=False).agg({"Statistics.Flights.Total":"mean"})
        
        fig = px.bar(
        plot_df,
        x="Time.Month Name",
        y="Statistics.Flights.Total",
        title=title,
        labels={"Statistics.Flights.Total":"Total Number of Flights","Time.Month Name":"Month"},
        template="simple_white",
        color_discrete_sequence=["cornflowerblue"]
    )
    else:
        plot_df = airline_df.groupby("Time.Month Name",as_index=False).agg({"Statistics.Flights.Total":"mean"})
    
        fig = px.bar(
        plot_df,
        x="Time.Month Name",
        y="Statistics.Flights.Total",
        title="Total flights each Month",
        labels={"Statistics.Flights.Total":"Total Number of Flights","Time.Month Name":"Month"},
        template="simple_white",
        color_discrete_sequence=["cornflowerblue"]
    )
    return fig

@app.callback(
    [Output("bubble", "figure"),
     Output("popup", "children"),
     Output("popup", "style")],
    Input("bubble-button", "n_clicks")
)

def show_bubble(n_clicks):
    if n_clicks is None or n_clicks == 0:
        return {'layout': {'xaxis': {'visible': False}, 'yaxis': {'visible': False}}}, None ,{'display': 'none'}
    elif n_clicks == 1:
        fig = px.scatter(
            airline_df,
            x="Statistics.Minutes Delayed.Weather",
            y="Statistics.# of Delays.Weather",
            size="Statistics.Minutes Delayed.Total",
            title="July has the highest number of Weather Delays",
            labels={"Statistics.Minutes Delayed.Weather": "Minutes Delayed for Weather",
                    "Statistics.# of Delays.Weather": "Number of Flights delayed for Weather"},
            color="Time.Month Name",
            hover_data="Airport.Code",
            template="simple_white"
        )
        return fig, None, {'display': 'none'}
    elif n_clicks % 2 != 0:
        fig = px.scatter(
            airline_df,
            x="Statistics.Minutes Delayed.Weather",
            y="Statistics.# of Delays.Weather",
            size="Statistics.Minutes Delayed.Total",
            title="July has the highest number of Weather Delays",
            labels={"Statistics.Minutes Delayed.Weather": "Minutes Delayed for Weather",
                    "Statistics.# of Delays.Weather": "Number of Flights delayed for Weather"},
            color="Time.Month Name",
            hover_data="Airport.Code",
            template="simple_white"
        )
        return fig, "Its back!! :)", {'display': 'block'}
    elif n_clicks > 1 and n_clicks % 2 == 0:  
        return {'layout': {'xaxis': {'visible': False}, 'yaxis': {'visible': False}}}, "You made the bubble disappear :(", {'display': 'block'}
    else:
        return {'layout': {'xaxis': {'visible': False}, 'yaxis': {'visible': False}}}, None, {'display': 'none'}
    

@app.callback(
    Output("box","figure"),
    Input("box-button","n_clicks"),
)

def show_box(n_clicks):
    if n_clicks is not None:
        agg_df = airline_df.groupby("Airport.Code")["Statistics.# of Delays.Weather"].sum().reset_index()
        agg_df_sorted = agg_df.sort_values(by="Statistics.# of Delays.Weather", ascending=False)
        top_10 = agg_df_sorted.head(5)
        fig = px.box(
            airline_df[airline_df["Airport.Code"].isin(top_10["Airport.Code"])],
            x="Airport.Code",
            y="Statistics.# of Delays.Weather",
            hover_data="Airport.Code",
            title="LaGuardia and Denver have the lowest average flights<br>delayed for weather",
            labels={"Statistics.# of Delays.Weather":"Number of Flights delayed for Weather","Airport.Code":"Airport"},
            template="simple_white",
            color_discrete_sequence=["cornflowerblue"]
    )
        return fig
    else:
        return {'layout': {'xaxis': {'visible': False}, 'yaxis': {'visible': False}}}
   
if __name__ == "__main__":
    app.run(debug=True)