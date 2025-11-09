#!/usr/bin/env python
# coding: utf-8

# # Prolem Set 2
# 
# **Author:** Your Study group number and names goes here
# 
# **Date:**
# 

# # Electricity, emissions, and GDP
# 

# In[75]:


##import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import geopandas as gpd
import wbgapi as wb
import country_converter as coco
import pyjanitor


# In[76]:


##define global color palette
fuel_color_palette = {
    # Fossil Fuels
    'coal': '#A0522D',      # Brown (Sienna)
    'oil': '#36454F',       # Dark Grey (Charcoal)
    'gas': '#6B9BD1',       # Soft Blue (like a natural gas flame)

    # Renewables
    'hydro': '#0077BE',     # Deep Blue (water)
    'solar': '#FFA500',     # Orange (sun, more distinct than yellow)
    'wind': '#A8D5E2',      # Light Sky Blue (air/sky)
    'biofuel': '#556B2F',    # Dark Green (biomass)
    'other_renewable': '#20B2AA', # Teal (general renewable)

    # Other
    'nuclear': '#E91E63'    # Pink/Magenta (a distinct, high-energy color)
}


# In[77]:


##import required data
co2_df = (
    pd.read_csv("https://ourworldindata.org/grapher/co-emissions-per-capita.csv?v=1&csvType=full&useColumnShortNames=true")
    .clean_names()
    .rename(columns={'emissions_total_per_capita': 'co2_per_capita', 'entity': 'country', 'code': 'iso_code'})
    .query("year >= 1990")
)

energy_df = (
    pd.read_csv("https://nyc3.digitaloceanspaces.com/owid-public/data/energy/owid-energy-data.csv")
    .clean_names()
    .query("year >= 1990")
    .dropna(subset=['iso_code'])
).rename(columns={ # We rename the long electricity source columns to be short and simple
        'biofuel_electricity': 'biofuel', 'coal_electricity': 'coal', 'gas_electricity': 'gas',
        'hydro_electricity': 'hydro', 'nuclear_electricity': 'nuclear', 'oil_electricity': 'oil',
        'other_renewable_exc_biofuel_electricity': 'other_renewable',
        'solar_electricity': 'solar', 'wind_electricity': 'wind'
    })


indicator_id = 'NY.GDP.PCAP.PP.KD'
gdp_percap_df = wb.data.DataFrame(
    indicator_id,
    time=range(1990, 2024),
    skipBlanks=True,
    columns='series'
)
gdp_percap_df = gdp_percap_df.reset_index().rename(columns={
    'economy': 'iso_code',
    'time': 'year',
    indicator_id: 'GDPpercap'
})
gdp_percap_df['year'] = gdp_percap_df['year'].str.replace('YR', '', regex=False).astype(int)



# In[78]:


#prepare data for analysis
energy_df_new = energy_df[['country', 'year', 'iso_code', 'population', 'gdp', 'biofuel', 'coal','gas', 'hydro', 'nuclear', 'oil', 'other_renewable', 'solar', 'wind']].\
            melt(id_vars=['country', 'year', 'iso_code', 'population', 'gdp'], var_name='source',value_name='value').\
            dropna(subset=['value', 'iso_code']).reset_index()
energy_df_new.head()


# In[79]:


#prepare data for analysis
data_1 = energy_df_new.merge(co2_df.drop(columns=['country']), on=['iso_code', 'year'], how='inner')
data = data_1.merge(gdp_percap_df, on=['iso_code', 'year'], how='inner')
data.head()


# In[97]:


#data visualization 1——Electricity Production Mix by Country and Year

country_options = data['country'].unique()
selected_country = st.selectbox("Select Country", country_options)
filtered_data = data[data['country'] == selected_country]

fig1 = px.area(filtered_data,x='year',y='value',color='source',
    labels={'year': 'Year','value': 'Electricity Production (TWh)','source': 'Energy Source'},
    title='Electricity Production Mix by Country and Year',
    color_discrete_sequence=list(fuel_color_palette.values()),
    category_orders={'source':['biofuel','coal','gas','hydro','nuclear','oil','other_renewable','solar','wind'][::-1]},
    template='plotly_white')
fig1.update_layout(legend=dict(traceorder='reversed'))
fig1.update_traces(line=dict(width=0))


# In[ ]:


co2_gdp_df = co2_df.merge(gdp_percap_df,on=['iso_code','year'],how='inner')


# In[102]:


#data visualization 2: the relationship between emission and gdp
fig2 = px.scatter(co2_gdp_df[co2_gdp_df['country']==selected_country], x='co2_per_capita', y='GDPpercap',
    labels={'GDPpercap':'GDP Per Capita','co2_per_capita':'CO2 Per Capita'},
    title='The Relationship between Emission and Economic Development',
    template='plotly_white')


# In[117]:


#Data Visualization 3: The relationship between electricity and gdp
data3 = data.groupby(['iso_code','year'])['value'].sum().reset_index().\
    rename(columns={'value':'elec'}).\
    merge(co2_gdp_df,on=['iso_code','year'],how='inner')
fig3 = px.scatter(data3[data3['country']==selected_country],x='elec',y='GDPpercap',
    labels={'GDPpercap':'GDP Per Capita','co2_per_capita':'CO2 Per Capita','elec':'Electricity Production (TWh)'},
    title='The Relationship between Electricity Production and Economic Development',
    template='plotly_white')


# In[118]:


st.plotly_chart(fig1, use_container_width=True)
col1, col2 = st.columns(2)
col1.plotly_chart(fig2, use_container_width=True)
col2.plotly_chart(fig3, use_container_width=True)

