import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy


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
dfs2['commissioning_year']=pd.to_datetime(dfs2['commissioning_date']).dt.year
dfs2=dfs2.drop(columns=['commissioning_date'])

dfs=deepcopy(dfs2)

left_column, right_column=st.columns([2,1])


en_l2_source = left_column.selectbox("Choose energy source", ["All"] + sorted(pd.unique(dfs.energy_source_level_2)), index=2)
years = sorted(pd.unique(dfs['commissioning_year']))
year = right_column.selectbox("Choose year", years, index=10)


st.title('Energy production in Switzerland')
st.header('Exploring the data')

if st.sidebar.checkbox("Show dataframe", True):
    st.subheader("My data set:")
    st.dataframe(data=dfs)


if en_l2_source == "All":
    rdf_l2=dfs
else:
   rdf_l2=dfs[dfs.energy_source_level_2==en_l2_source]

if st.sidebar.checkbox("Show Energy level 2 dataframe", True):
    st.subheader("Energy level 2  data set:")
    st.dataframe(data=rdf_l2.drop(columns=['energy_source_level_3','electrical_capacity','energy_source_level_1']))

#Calculation of total production and total plants for energy source level 2

def generate_plot_l2(en_l2_source, dfs):
    if en_l2_source == "All":
        rdf_l2 = dfs
    else:
        rdf_l2 = dfs[dfs.energy_source_level_2 == en_l2_source]

    rdf_l2_plot = rdf_l2.groupby('commissioning_year').agg(total_production=('production', 'sum'), total_plants=('production', 'count')).reset_index()

    # Create the scatter traces for each subplot
    scatter_trace1 = go.Scatter(x=rdf_l2_plot['commissioning_year'], y=rdf_l2_plot['total_production'], mode='lines+markers', name='Total Production (MWh)', marker=dict(color='blue'), line=dict(color='blue'))
    scatter_trace2 = go.Scatter(x=rdf_l2_plot['commissioning_year'], y=rdf_l2_plot['total_plants'], mode='lines+markers', name='Total number of plants', marker=dict(color='red'), line=dict(color='red'), yaxis='y2')

    # Create the subplot figure
    fig = go.Figure([scatter_trace1, scatter_trace2])

    # Update layout including the value of en_l2_source in the title
    title = f"Comparison of Total Production and Total Number of Plants for {en_l2_source}"
    fig.update_layout(
        xaxis_title='Commissioning Year',
        title=title,
        yaxis=dict(title='Total Production (MWh)'),
        yaxis2=dict(title='Total Number of Plants', overlaying='y', side='right')
    )

    # Show the figure using Streamlit's Plotly support
    st.plotly_chart(fig)
 
generate_plot_l2(en_l2_source, dfs)

#print value of en_l2_source
st.write(f"Value of en_l2_source: {en_l2_source}")


def generate_choropleth_l2(en_l2_source, year, dfs, geojson):
    # Correct the column name 'energy_source_level2' to 'energy_source_level_2'
    df_canton_prod = dfs[(dfs.energy_source_level_2 == en_l2_source) & (dfs['commissioning_year'] == year)].groupby('CantonNumericCode').agg(total_production=('production', 'sum')).reset_index()

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
        )
    )
    st.plotly_chart(choropleth_fig)
   
generate_choropleth_l2(en_l2_source, year, dfs, geojson)

st.write("# Explore the energy sources in Switzerland", unsafe_allow_html=True)

# Grouping and aggregating data
dfs_l2_cantons = dfs.groupby(['CantonName', 'energy_source_level_2']).agg(total_production=('production', 'sum')).reset_index()

# Sorting values by total_production
dfs_l2_cantons = dfs_l2_cantons.sort_values(by='total_production', ascending=False)

# Creating the Plotly figure
fig3 = px.bar(dfs_l2_cantons, y='CantonName', x='total_production', color='energy_source_level_2', barmode='stack', height=800, width=1200)
# Change x and y axis names
fig3.update_xaxes(title_text='Total Production (MWh)')
fig3.update_yaxes(title_text='Canton Name')

# increase font size of axis labels
fig3.update_layout(xaxis=dict(title=dict(font=dict(size=20))), yaxis=dict(title=dict(font=dict(size=20))))

# Displaying the figure using Streamlit
st.plotly_chart(fig3)

