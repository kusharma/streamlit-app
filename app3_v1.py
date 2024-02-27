import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy
import numpy as np

st.set_page_config(layout="wide")

@st.cache_data
def load_data(path): # whatever comes out of this function into cache
    df=pd.read_csv(path)
    return df

with open('data/georef-switzerland-kanton.geojson') as f:
    geojson= json.load(f)

df_raw=load_data(path='data/renewable_power_plants_CH.csv')
df_en=deepcopy(df_raw) # so deep copy is stored in the cache and will not be changed, we work only with the copy

swiss_cantons = load_data(path='data/swiss_cantons.csv')  
# keep only first 3 columnns
swiss_cantons = swiss_cantons.iloc[:,0:3]

df_en = df_en.drop(columns=['project_name', 'company', 'nuts_1_region', 'nuts_2_region', 'data_source', 'nuts_3_region', 'address','municipality', 'municipality_code','technology','postcode'])
dfs2=pd.merge(df_en, swiss_cantons, left_on='canton', right_on='Canton', how='left')
# change commisioning date to commsioning year
dfs2['year']=pd.to_datetime(dfs2['commissioning_date']).dt.year
dfs2=dfs2.drop(columns=['commissioning_date'])
# Divide production by 1e9 to get MWh
dfs2['production'] = dfs2['production'] / 1e6
dfs2['CantonName']=dfs2['CantonName'].str.strip().str.split(' |-').str[0]

dfs=deepcopy(dfs2)

left_column, right_column=st.columns([1,1])


en_l2_source = left_column.selectbox("Choose energy source", ["All"] + sorted(pd.unique(dfs.energy_source_level_2)), index=2)
years = sorted(pd.unique(dfs['year']))
year = right_column.selectbox("Choose year", years, index=10)



st.title('Where is energy produced in Switzerland')
# st.header('Exploring the data')

# if st.sidebar.checkbox("Show dataframe", False):
#     st.subheader("My data set:")
#     st.dataframe(data=dfs)


if en_l2_source == "All":
    rdf_l2=dfs
else:
   rdf_l2=dfs[dfs.energy_source_level_2==en_l2_source]

# if st.sidebar.checkbox("Show Energy level 2 dataframe", False):
#     st.subheader("Energy level 2  data set:")
#     st.dataframe(data=rdf_l2.drop(columns=['energy_source_level_3','electrical_capacity','energy_source_level_1']))

#Calculation of total production and total plants for energy source level 2

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

def generate_plot_l2(en_l2_source, dfs):
    if en_l2_source == "All":
        rdf_l2 = dfs
    else:
        rdf_l2 = dfs[dfs.energy_source_level_2 == en_l2_source]

    rdf_l2_plot = rdf_l2.groupby('year').agg(total_production=('production', 'sum'), total_plants=('production', 'count')).reset_index()

    # Create the scatter traces for each subplot
    scatter_trace1 = go.Scatter(x=rdf_l2_plot['year'], y=rdf_l2_plot['total_production'], mode='lines+markers', name='Total Production (MWh)', marker=dict(color='blue'), line=dict(color='blue'))
    scatter_trace2 = go.Scatter(x=rdf_l2_plot['year'], y=rdf_l2_plot['total_plants'], mode='lines+markers', name='Total number of plants', marker=dict(color='red'), line=dict(color='red'), yaxis='y2')

    # Create the subplot figure
    fig = go.Figure([scatter_trace1, scatter_trace2])

    # Update layout including the value of en_l2_source in the title
    title = f"Comparison of Total Production and Total Number of Plants for {en_l2_source}"
    fig.update_layout(
        xaxis_title='Commissioning Year',
        title=title,
        yaxis=dict(title='Total Production (MWh)'),
        yaxis2=dict(title='Total Number of Plants', overlaying='y', side='right'),
        width=600,  # Width in pixels
        height=400,
    )

    return fig

def generate_choropleth_l2(en_l2_source, year, dfs, geojson):
    # Correct the column name 'energy_source_level2' to 'energy_source_level_2'
    df_canton_prod = dfs[(dfs.energy_source_level_2 == en_l2_source) & (dfs['year'] == year)].groupby('CantonNumericCode').agg(total_production=('production', 'sum')).reset_index()

    choropleth_fig = px.choropleth_mapbox(
        data_frame=df_canton_prod,
        geojson=geojson,
        locations='CantonNumericCode',
        featureidkey="properties.kan_code",
        color='total_production',
        mapbox_style="carto-positron",
        zoom=6,
        center={"lat": 46.8, "lon": 8.2},
        opacity=0.5,
        labels={'total_production': f'Total Production in MWh in {year}'}
    )

    # Update layout of choropleth map subplot
    choropleth_fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(
            title=f'Total Production<br>in MWh in {year}'
        ), width=600, height=400
    )

    return choropleth_fig

# Assuming en_l2_source, year, dfs, and geojson are defined
# st.write(f"Value Energy Source: {en_l2_source}")

# Use columns to display plots side by side
col1, col2 = st.columns(2)

with col1:
    fig1 = generate_plot_l2(en_l2_source, dfs)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = generate_choropleth_l2(en_l2_source, year, dfs, geojson)
    st.plotly_chart(fig2, use_container_width=True)


#st.write("# Explore the energy sources in Switzerland", unsafe_allow_html=True)

# Grouping and aggregating data
dfs_l2_cantons = dfs.groupby(['CantonName', 'energy_source_level_2']).agg(total_production=('production', 'sum')).reset_index()

# Sorting values by total_production
dfs_l2_cantons = dfs_l2_cantons.sort_values(by='total_production', ascending=False)

# Creating the Plotly figure
fig3 = px.bar(dfs_l2_cantons, y='CantonName', x='total_production', color='energy_source_level_2', 
              barmode='stack',labels={'energy_source_level_2': 'Energy Source'})
# Change x and y axis names
fig3.update_xaxes(title_text='Total Production (MWh)')
fig3.update_yaxes(title_text='Canton Name')

# increase font size of axis labels
fig3.update_layout(xaxis=dict(title=dict(font=dict(size=20))), 
                   yaxis=dict(title=dict(font=dict(size=20))), 
                    legend=dict(yanchor="bottom",y=0.8, xanchor="right",x=0.8,font=dict(size=14)),width=600, height=600)

# Displaying the figure using Streamlit
st.plotly_chart(fig3, use_container_width=False)

df_icons=dfs[['lon','lat','energy_source_level_2','CantonName']]
df_icons=dfs.dropna()

# Example DataFrame loading or creation here
# Ensure df_icons is already loaded or created with the necessary columns

color_discrete_map = {
    'Solar': 'magenta',
    'Wind': 'red',
    'Bioenergy': 'limegreen',
    'Hydro': 'purple'
}

fig4 = px.scatter_mapbox(df_icons,
                        lat="lat",
                        lon="lon",
                        color="energy_source_level_2",
                        color_discrete_map=color_discrete_map,  # Use the explicit color map
                        hover_name="CantonName",
                        hover_data=["CantonName", "energy_source_level_2"],
                        zoom=7,
                        height=600)

fig4.update_layout(mapbox_style="open-street-map")
fig4.update_traces(marker=dict(size=10))


# Display the figure in Streamlit
st.plotly_chart(fig4, use_container_width=True)  # Set to True for responsive width



#st.write("# Total yearly electrical capacity", unsafe_allow_html=True)

df_el = dfs.groupby(['CantonName', 'CantonNumericCode', 'year']).agg(yearly_capacity=('electrical_capacity', 'sum')).reset_index()
df_el = df_el.sort_values(by=['year', 'yearly_capacity'], ascending=[True, False])

# Assuming you have sorted_df DataFrame containing the sorted data
fig5 = px.bar(df_el, x='CantonName', y='yearly_capacity', animation_frame='year',
             title=" Electrical Capacity from cantons",
             labels={'yearly_capacity': 'Electrical yearly capacity (billion kWh)', 'CantonName': 'Canton Name'},
             range_y=[0, df_el['yearly_capacity'].max()*1.1])  # Adjust range_y for better visualization

fig5.update_layout(xaxis={'categoryorder':'total descending'})


fig6 = px.choropleth_mapbox(
    data_frame=df_el,
    geojson=geojson,
    locations='CantonNumericCode',
    featureidkey="properties.kan_code",
    color='yearly_capacity',
    mapbox_style="carto-positron",
    zoom=6,
    center={"lat": 46.8, "lon": 8.2},
    opacity=0.5,
    animation_frame='year',  # Add animation frame based on 'year' column
    color_continuous_scale=px.colors.sequential.Viridis,  # Adjust color scale as needed
    title="Evolution of electrical capacity",
    labels={'yearly_capacity': 'billion kWh', 'CantonNumericCode': 'Canton Numeric Code'}
)

fig6.update_layout(
    margin={"r":0,"t":30,"l":0,"b":0},
    mapbox=dict(
        center={"lat": 46.8, "lon": 8.2},
        zoom=6
    )
)

# Use columns to display plots side by side
col3, col4 = st.columns(2)

with col3:
    # Display fig5 in the first column
    st.plotly_chart(fig5, use_container_width=True)

with col4:
    # Display fig6 in the second column
    st.plotly_chart(fig6, use_container_width=True)

# Initialize or get the session state variable for animation
if 'show_animation' not in st.session_state:
    st.session_state.show_animation = False

# Button to toggle animation
if st.button('Toggle Animation'):
    st.session_state.show_animation = not st.session_state.show_animation

if st.session_state.show_animation:
    # Assuming fig5 and fig6 are defined with animation
    st.plotly_chart(fig5)
    st.plotly_chart(fig6)
else:
    st.write("Click the button to show animations.")