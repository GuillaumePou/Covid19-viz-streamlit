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

@st.cache(allow_output_mutation=True)
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
    df['daysAfter10Deaths'] = df[df.deathsCum > 10].groupby('geoId').deathsCum.rank(method="first", ascending=True)
    return(df)

df = processData(retrieveDF(today).copy())

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
    ('Charts', 'Map', 'HeatMap')
)         

lastDay = df.dateRep.max()
totalCases = df[df.dateRep==lastDay].casesCum.sum()
totalDeaths = df[df.dateRep==lastDay].deathsCum.sum()

st.sidebar.markdown("Date: \n {}".format(date.today()))
st.sidebar.markdown("Total cases: {}".format(totalCases))
st.sidebar.markdown("Total deaths: {}".format(totalDeaths))

scale = 'linear'

if typeSelectbox == "Charts":
    if st.checkbox('All Countries'):
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
    else:
        indexdf15 =  df.groupby('geoId').casesCum.max().sort_values(ascending = False)[0:15].index
        df15 = df[df.geoId.isin(indexdf15)]
        if st.checkbox('Cummulative'):
        
            if st.checkbox('log scale'):
                
                chartDeaths = chart(df15, 'dateRep', 'deathsCum', 'countriesAndTerritories', 'log')
                chartCases = chart(df15, 'dateRep', 'casesCum', 'countriesAndTerritories', 'log')
                
                st.altair_chart(chartDeaths, use_container_width=True)
                st.altair_chart(chartCases, use_container_width=True)
            
            else:
                chartDeaths = chart(df15, 'dateRep', 'deathsCum', 'countriesAndTerritories')
                chartCases = chart(df15, 'dateRep', 'casesCum', 'countriesAndTerritories')
                
                st.altair_chart(chartDeaths, use_container_width=True)
                st.altair_chart(chartCases, use_container_width=True)    
            
            if st.checkbox('Fatality rate'):
                chartFatality = chart(df15, 'dateRep', 'fatalityRate', 'countriesAndTerritories')
                st.altair_chart(chartFatality, use_container_width=True)
    
        else:
            chartDeaths = chart(df15, 'dateRep', 'deaths', 'countriesAndTerritories')
            chartCases = chart(df15, 'dateRep', 'cases', 'countriesAndTerritories')
            
            st.altair_chart(chartDeaths, use_container_width=True)
            st.altair_chart(chartCases, use_container_width=True)

elif typeSelectbox == "Map":
    


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



elif typeSelectbox == "HeatMap":
    indexdf15 =  df.groupby('geoId').casesCum.max().sort_values(ascending = False)[0:15].index
    df15 = df[df.geoId.isin(indexdf15)]
    
    # make heatmap on nb of cum death
    heatmapDeath = (
        alt.Chart(df15)
        .mark_rect()
        .encode(
            alt.X("dateRep"),
            alt.Y("countriesAndTerritories"),
            alt.Color("deathsCum", scale=alt.Scale(scheme="lightmulti")),
            tooltip=["dateRep", "countriesAndTerritories", "deathsCum"],
        )
        .interactive()
    )

    st.altair_chart(heatmapDeath, use_container_width=True)

    # make heatmap on nb of cum death since 10 deaths
    heatmapDeathAfter10 = (
        alt.Chart(df15)
        .mark_rect()
        .encode(
            alt.X("daysAfter10Deaths"),
            alt.Y("countriesAndTerritories"),
            alt.Color("deathsCum", scale=alt.Scale(scheme="lightmulti")),
            tooltip=["daysAfter10Deaths", "countriesAndTerritories", "deathsCum"],
        )
        .interactive()
    )

    st.altair_chart(heatmapDeathAfter10, use_container_width=True)



