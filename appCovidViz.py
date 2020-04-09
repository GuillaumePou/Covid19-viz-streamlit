# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 12:33:21 2020

@author: guillaume
"""

#%% import packages
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import plotly.express as px
from datetime import date

today = date.today().day

#%% Intialize paths

@st.cache
def retrieveDF(today):
    from io import StringIO
    import requests
    urlCovid19 = "https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"
    df = pd.read_csv(StringIO(requests.get(urlCovid19).text), sep=",")
    return df

#%% load df and process

@st.cache
def processData(df):
#    df = pd.read_csv(path2csv, sep=",", encoding='latin-1')
    df.dateRep = pd.to_datetime(df.dateRep, format="%d/%m/%Y")
    
    #add cumulative deaths and confirmed cases
    df['deathsCum'] = df.sort_values('dateRep',ascending=True).groupby('geoId').deaths.cumsum()
    df['casesCum'] = df.sort_values('dateRep',ascending=True).groupby('geoId').cases.cumsum()
    df["fatalityRate"] = df.deathsCum / df.casesCum
    df["fatalityRate"] = df["fatalityRate"].where(df["fatalityRate"] !=1)
    # create a new index based from day after 10 deaths
    df['daysAfter10days'] = df[df.deathsCum > 10].groupby('geoId').deaths.rank(method="first", ascending=True)
    return(df)

df = processData(retrieveDF(today))

#%% functions

def chart(df,x,y,z,scale='linear'):
    if scale=='linear':
        scaleAlt =  alt.Scale(type=scale)
    else:
        scaleAlt = alt.Scale(type="log", domain=[1, 1000000], clamp=True)
    return (
    alt.Chart(df)
    .mark_line(point=True)
    .encode(
        alt.X(x),
        alt.Y(y, scale=scaleAlt),
        alt.Color(z),
        tooltip=[x, y, z],
    )
    .interactive()
    )


#%% the GUI

st.title("Covid 19 vizualization")

#sidebar
# Add a selectbox to the sidebar: return a value
typeSelectbox = st.sidebar.selectbox(
    'How would you like to display the data set',
    ('charts', 'map')
)         

lastDay = df.dateRep.max()
totalCases = df[df.dateRep==lastDay].casesCum.sum()
totalDeaths = df[df.dateRep==lastDay].deathsCum.sum()

st.sidebar.markdown("Day \n {}".format(lastDay))
st.sidebar.markdown("Total cases: {}".format(totalCases))
st.sidebar.markdown("Total deaths: {}".format(totalDeaths))

scale = 'linear'

if typeSelectbox == "charts":
    if st.checkbox('Cummulative'):
    
        if st.checkbox('log scale'):
            
            chartDeaths = chart(df, 'dateRep', 'deathsCum', 'countriesAndTerritories', 'log')
            chartCases = chart(df, 'dateRep', 'casesCum', 'countriesAndTerritories', 'log')
            
            st.altair_chart(chartDeaths, use_container_width=True)
            st.altair_chart(chartCases, use_container_width=True)
        
        else:
            chartDeaths = chart(df, 'dateRep', 'deathsCum', 'countriesAndTerritories')
            chartCases = chart(df, 'dateRep', 'casesCum', 'countriesAndTerritories')
            
            st.altair_chart(chartDeaths, use_container_width=True)
            st.altair_chart(chartCases, use_container_width=True)    
        
        if st.checkbox('Fatality rate'):
            chartFatality = chart(df, 'dateRep', 'fatalityRate', 'countriesAndTerritories')
            st.altair_chart(chartFatality, use_container_width=True)

    else:
        chartDeaths = chart(df, 'dateRep', 'deaths', 'countriesAndTerritories')
        chartCases = chart(df, 'dateRep', 'cases', 'countriesAndTerritories')
        
        st.altair_chart(chartDeaths, use_container_width=True)
        st.altair_chart(chartCases, use_container_width=True)

elif typeSelectbox == "map":
    


#%%

    # nbDaySinceOutbreak = df.dateRep.max() - df.dateRep.min()
    # date = st.slider('Date', 0, 1, nbDaySinceOutbreak)
    
    
    if st.checkbox('not logarithmic scale'):
        dfm = df[df['dateRep']==lastDay]
        
    else:
        dfm = df[df['dateRep']==lastDay]
        dfm["deathsCum"] = np.log10(dfm.deathsCum)
        
    fig = px.choropleth(dfm, locations="countryterritoryCode",
                        color="deathsCum", # lifeExp is a column of gapminder
                        hover_name="countriesAndTerritories", # column to add to hover information
                        color_continuous_scale='Reds')
    fig.update_layout(
    title_text = 'Map of covid 19'
    )
    st.plotly_chart(fig, use_container_width=True)








