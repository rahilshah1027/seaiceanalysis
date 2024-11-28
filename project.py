import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

north_ice_data = pd.read_csv("n_ice_data.csv", skiprows=2)
south_ice_data = pd.read_csv("s_ice_data.csv", skiprows=2)

north_ice_data.columns = ['Year', 'Month', 'Day', 'Extent', 'Missing', 'Source Data']
north_ice_data['Date'] = pd.to_datetime(north_ice_data[['Year', 'Month', 'Day']])
north_ice_data.set_index('Date', inplace=True)

south_ice_data.columns = ['Year', 'Month', 'Day', 'Extent', 'Missing', 'Source Data']
south_ice_data['Date'] = pd.to_datetime(south_ice_data[['Year', 'Month', 'Day']])
south_ice_data.set_index('Date', inplace=True)

north_annual_averages = north_ice_data.groupby("Year")["Extent"].mean()
south_annual_averages = south_ice_data.groupby("Year")["Extent"].mean()
# print(north_annual_averages)
# print(south_annual_averages)

n_temp = pd.read_csv("n_temp.csv", skiprows=4)
n_temp['Year'] = n_temp['Date'].astype(str).str[:4]
n_temp['Month'] = n_temp['Date'].astype(str).str[4:]
north_annual_temps= n_temp.groupby('Year')['Anomaly'].mean()
#print(north_annual_temps)

s_temp = pd.read_csv("s_temp.csv", skiprows=4)
s_temp['Year'] = s_temp['Date'].astype(str).str[:4]
s_temp['Month'] = s_temp['Date'].astype(str).str[4:]
south_annual_temps= s_temp.groupby('Year')['Anomaly'].mean()
#print(south_annual_temps)

north_annual_averages.index = north_annual_averages.index.astype(int)
south_annual_averages.index = south_annual_averages.index.astype(int)
north_annual_temps.index = north_annual_temps.index.astype(int)
south_annual_temps.index = south_annual_temps.index.astype(int)

north_combined = pd.DataFrame({
    'Year': north_annual_averages.index,
    'Sea Ice Extent': north_annual_averages.values
}).merge(pd.DataFrame({
    'Year': north_annual_temps.index,
    'Temperature Anomaly': north_annual_temps.values
}), on='Year', how='inner')

south_combined = pd.DataFrame({
    'Year': south_annual_averages.index,
    'Sea Ice Extent': south_annual_averages.values
}).merge(pd.DataFrame({
    'Year': south_annual_temps.index,
    'Temperature Anomaly': south_annual_temps.values
}), on='Year', how='inner')

def normalize_data(data):
    data['Normalized Sea Ice Extent'] = (
        data['Sea Ice Extent'] - data['Sea Ice Extent'].min()
    ) / (data['Sea Ice Extent'].max() - data['Sea Ice Extent'].min())
    data['Normalized Temperature Anomaly'] = (
        data['Temperature Anomaly'] - data['Temperature Anomaly'].min()
    ) / (data['Temperature Anomaly'].max() - data['Temperature Anomaly'].min())
    return data

def plot_normalized(data, title):
    fig = px.line(
        data,
        x='Year',
        y=['Normalized Sea Ice Extent', 'Normalized Temperature Anomaly'],
        title=title,
        labels={'value': 'Normalized Values', 'variable': 'Metric'},
    )
    return fig

def plot_dual_axis(data, title):
    fig = px.line(title=title)
    fig.add_scatter(x=data['Year'], y=data['Sea Ice Extent'], mode='lines', name='Sea Ice Extent')
    fig.add_scatter(x=data['Year'], y=data['Temperature Anomaly'], mode='lines', name='Temperature Anomaly', yaxis='y2')
    fig.update_layout(
        yaxis=dict(title="Sea Ice Extent (10^6 sq km)"),
        yaxis2=dict(title="Temperature Anomaly (°C)", overlaying='y', side='right'),
        xaxis=dict(title="Year"),
        title=title
    )
    return fig

st.set_page_config(layout="wide")
st.title("Comparing Sea Ice Extent and Temperature Anomalies in Northern and Southern Hemispheres")

# Add unit explanation
st.markdown("""
### Units:
- **Sea Ice Extent**: Measured in \(10^6\) square kilometers.
- **Temperature Anomaly** (Difference from an average/baseline temperature): Measured in Celsius (°C).
    - Positive means that observed temperature was warmer than baseline
    - Negative means that observed temperature was colder than baseline
""")

# Create two columns to display the hemispheres side by side
col1, col2 = st.columns([10, 10])

# Display data and plots in columns
with col1:
    st.header("Northern Hemisphere")
    normalized_data_north = normalize_data(north_combined)
    option = st.radio(
        "Choose Visualization for Northern Hemisphere",
        ["Normalized Line Chart", "Dual-Axis Chart"],
        key='north'
    )
    if option == "Normalized Line Chart":
        st.plotly_chart(plot_normalized(normalized_data_north, "Northern Hemisphere: Normalized Sea Ice Extent vs Temperature Anomaly"))
    elif option == "Dual-Axis Chart":
        st.plotly_chart(plot_dual_axis(north_combined, "Northern Hemisphere: Sea Ice Extent vs Temperature Anomaly (Dual Axis)"))
    if st.checkbox("Show Raw Data for Northern Hemisphere", key='north_data'):
        st.write(north_combined)
    correlation_north = north_combined['Sea Ice Extent'].corr(north_combined['Temperature Anomaly'])
    st.write(f"Correlation between Sea Ice Extent and Temperature Anomaly for Northern Hemisphere: **{correlation_north:.4f}**")

with col2:
    st.header("Southern Hemisphere")
    normalized_data_south = normalize_data(south_combined)
    option = st.radio(
        "Choose Visualization for Southern Hemisphere",
        ["Normalized Line Chart", "Dual-Axis Chart"],
        key='south'
    )
    if option == "Normalized Line Chart":
        st.plotly_chart(plot_normalized(normalized_data_south, "Southern Hemisphere: Normalized Sea Ice Extent vs Temperature Anomaly"))
    elif option == "Dual-Axis Chart":
        st.plotly_chart(plot_dual_axis(south_combined, "Southern Hemisphere: Sea Ice Extent vs Temperature Anomaly (Dual Axis)"))
    if st.checkbox("Show Raw Data for Southern Hemisphere", key='south_data'):
        st.write(south_combined)
    correlation_south = south_combined['Sea Ice Extent'].corr(south_combined['Temperature Anomaly'])
    st.write(f"Correlation between Sea Ice Extent and Temperature Anomaly for Southern Hemisphere: **{correlation_south:.4f}**")        

st.markdown("""
### Summary of Findings

In these graphs, I compared the relationship between sea ice extent and temperature anomalies from 1978 to 2024 for both the Northern and Southern Hemispheres.

- **Northern Hemisphere**: 
  - I observed a **decreasing trend** in sea ice extent over the years, consistent with increasing global temperatures.
  - A correlation of -0.93 between **Sea Ice Extent** and **Temperature Anomaly** suggests that as the temperature rises, sea ice extent decreases.
  - This is directly inline with what we studied in class where we saw that with current temperatures, during the summer the sea ice extent becomes so small that new passages such as the Northwest and Northeast passage are capable of moving through.

- **Southern Hemisphere**: 
  - I observed similiar trends in the Southern Hemisphere with **decreasing sea ice extent** and **rising temperature anomalies**.
  - While the correlation between between **Sea Ice Extent** and **Temperature Anomaly** in the Southern Hemisphere is only -0.31 it also points to a similar trend with whats happening in the Northern Hemisphere.

### Conclusion:
These graphs clearly show us a **negative correlation** between sea ice extent and temperature anomalies in both hemispheres. This suggests that as global temperatures continue to rise, sea ice is diminishing, which could have significant implications for global climate patterns, ocean currents, and marine ecosystems. 
""")