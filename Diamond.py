import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# Titel
st.markdown(
    "<h1 style='text-align: center;'>Diamantanalys</h1>",
    unsafe_allow_html=True
)

# Ladda och städa data
@st.cache_data
def clean_diamond_data():
    df = pd.read_csv("diamonds.csv")
    df = df.dropna(subset=['cut', 'color', 'clarity', 'price', 'carat', 'x', 'y', 'z', 'depth'])
    df = df[(df['x'] > 0) & (df['y'] > 0) & (df['z'] > 0)]
    df = df[(df['x'] <= 15) & (df['y'] <= 15) & (df['z'] <= 15)]
    df = df[~((df['carat'] < 1) & (df['z'] > 10))]
    df['depth_calc'] = (df['z'] / ((df['x'] + df['y']) / 2)) * 100
    df['depth_diff'] = abs(df['depth_calc'] - df['depth'])
    df = df[df['depth_diff'] <= 1]
    return df

df = clean_diamond_data()

# Visa data
if st.checkbox("Visa första 5 raderna i datan"):
    st.write(df.head())

# Interaktiv scatterplot med hover
fig = px.scatter(
    df,
    x='carat',
    y='price',
    hover_data=['cut', 'color', 'clarity', 'price'],
    title='Pris i förhållande till vikt (carat)',
    opacity=0.4
)

st.plotly_chart(fig, use_container_width=True)