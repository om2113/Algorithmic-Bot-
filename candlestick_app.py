import streamlit as st 
import pandas as pd
from datetime import datetime

from bokeh.plotting import figure, column

import talib

#st.set_page_config(layout ="wide", page_title ="Candlestick App with Technical Indicators")
st.set_page_config(layout="wide")
st.title("Candlestick App with Technical Indicators")

@st.cache_data
def load_dataset(start_date, end_date):
    apple_df = pd.read_csv("AAPL.csv")  
    #print(apple_df.columns)
    apple_df["Date"] = pd.to_datetime(apple_df["Date"], format="%d-%m-%Y")
    apple_df["BarColor"] = apple_df.apply(lambda row: "red" if row["Open"] > row["Close"] else "green", axis=1)
    apple_df["Date_str"] = apple_df["Date"].astype(str)
    ## Filter dataset based on start and end dates
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    apple_df = apple_df[(apple_df["Date"] >= start_date) & (apple_df["Date"] <= end_date)]
    ## Calculate Various Indicators
    apple_df["SMA"] = talib.SMA(apple_df.Close, timeperiod=3)
    apple_df["MA"] = talib.MA(apple_df.Close, timeperiod=3)
    apple_df["EMA"] = talib.EMA(apple_df.Close, timeperiod=3)
    apple_df["WMA"] = talib.WMA(apple_df.Close, timeperiod=3)
    apple_df["RSI"] = talib.RSI(apple_df.Close, timeperiod=3)
    apple_df["MOM"] = talib.MOM(apple_df.Close, timeperiod=3)
    apple_df["DEMA"] = talib.DEMA(apple_df.Close, timeperiod=3)
    apple_df["TEMA"] = talib.TEMA(apple_df.Close, timeperiod=3)
   
    return apple_df

#apple_df = load_dataset(start_dt, end_dt)
indicator_colors = {"SMA": "orange", "EMA": "violet", "WMA": "blue", "RSI": "yellow", "MOM": "black", "DEMA": "red", "MA": "tomato",
                    "TEMA": "dodgerblue"}

def create_chart(df, close_line=False, include_vol=False, indicators=[]):
    ## Candlestick Pattern Logic
    candle = figure(x_axis_type="datetime", outer_height=500, x_range=(df.Date.values[0], df.Date.values[-1]),
                 tooltips=[("Date", "@Date_str"), ("Open", "@Open"), ("High", "@High"), ("Low", "@Low"), ("Close", "@Close")],)

    candle.segment("Date", "Low", "Date", "High", color="black", line_width=0.5, source=df)
    candle.segment("Date", "Open", "Date", "Close", line_color="BarColor", line_width=2 if len(df)>100 else 6, source=df)

    candle.xaxis.axis_label="Date"
    candle.yaxis.axis_label="Price ($)"

    ## Close Price Line
    if close_line:
        candle.line("Date", "Close", color="black", source=df)

    for indicator in indicators:
        candle.line("Date", indicator, color=indicator_colors[indicator], line_width=2, source=df, legend_label=indicator)

    ## Volume Bars Logic
    volume = None
    if include_vol:
        volume = figure(x_axis_type="datetime", plot_height=150, x_range=(df.Date.values[0], df.Date.values[-1]),)
        volume.segment("Date", 0, "Date", "Volume",  line_width=2 if len(df)>100 else 6, line_color="BarColor", alpha=0.8, source=df)
        volume.yaxis.axis_label="Volume"

    return column(children=[candle, volume], sizing_mode="scale_width") if volume else candle

talib_indicators = ["MA", "EMA", "SMA", "WMA", "RSI", "MOM", "DEMA", "TEMA"]
## Dashboard
st.sidebar.markdown("#### Date Range Selection")

col1, col2 = st.sidebar.columns(2, gap="medium")
with col1:
    start_dt = st.date_input("Start:", value=datetime(2010, 1, 4), min_value=datetime(2010, 1, 1), max_value=datetime(2023, 12, 30))
with col2:
    end_dt = st.date_input("End:", value=datetime(2023, 12, 30), min_value=datetime(2010, 2, 1), max_value=datetime(2023, 12, 30))


# Now `start_dt` and `end_dt` are defined
apple_df = load_dataset(start_dt, end_dt)

close_line = st.sidebar.checkbox("Close Prices")
volume = st.sidebar.checkbox("Include Volume")

indicators = st.sidebar.multiselect(label="Technical Indicators", options=talib_indicators)

sub_df = apple_df.set_index("Date").loc[str(start_dt):str(end_dt)]
sub_df = sub_df.reset_index()

st.bokeh_chart(create_chart(sub_df, close_line, volume, indicators), use_container_width=True)