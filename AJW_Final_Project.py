"""
Class: CS 230
Name: AJ Worsley
Description: Final Project
"""

import streamlit as st
import pydeck as pdk
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random as rd
from PIL import Image
import plotly.express as px

pd.set_option("display.max_rows", None, "display.max_columns", None, 'display.width', None, 'max_colwidth', None)

df_crime = pd.read_csv("BostonCrime2021_7000_sample.csv")
df_districts = pd.read_csv("BostonPoliceDistricts.csv")


# Function if region names needed
def regions_tuple():
    sdf_districts = df_districts.sort_values(["District Name"], ascending=[True])
    sdf_districts = sdf_districts.dropna()

    regions = tuple(zip(sdf_districts["District"], sdf_districts["District Name"]))
    return regions


# User interface for web application
logo = Image.open("Boston Police Logo.jpg")
st.image(logo, width=200)

st.title("2021 Boston Crime")
select_display = st.selectbox("What information would you like to access?",
                              ["", "Locations", "Times of Day", "Common Types"])

# Code for location data
if select_display == "Locations":
    # UI
    location_display = st.sidebar.radio("Which data would you like to access?", ["", "Map", "Amount per District"])

    # Code for maps of crime locations
    if location_display == "Map":
        sdf_crime_map = df_crime.loc[:, ["OFFENSE_DESCRIPTION", "Lat", "Long"]]
        sdf_crime_map = sdf_crime_map.dropna()

        sdf_crime_map.rename(columns={"Lat": "lat", "Long": "lon"}, inplace=True)

        # Creating variable maps as shown in class
        offenses_list = []
        for c in df_crime.OFFENSE_DESCRIPTION:
            if c.lower().title().strip() not in offenses_list:
                offenses_list.append(c.lower().title().strip())

        sdf_list = []
        for c in offenses_list:
            sdf = sdf_crime_map[sdf_crime_map["OFFENSE_DESCRIPTION"].str.lower().str.title().str.strip() == c]
            sdf_list.append(sdf)

        layer_list = []
        for sdf in sdf_list:
            layer = pdk.Layer(type='ScatterplotLayer',
                              data=sdf,
                              get_position="[lon, lat]",
                              get_radius=50,
                              get_color=[rd.randint(0, 255), rd.randint(0, 255), rd.randint(0, 255)],
                              pickable=True)
            layer_list.append(layer)

        offenses_list.insert(0, "")

        type_selection = st.sidebar.selectbox("Which type of crime would you like to search for?", offenses_list)

        st.title("Locations of Crime in Boston")

        view_state = pdk.ViewState(latitude=42.338357,
                                   longitude=-71.070911,
                                   zoom=12,
                                   pitch=0)

        tool_tip = {"html": "Crime Type:<br/> <b>{OFFENSE_DESCRIPTION}</b>",
                    "style": {"backgroundColor": "BlueViolet",
                              "color": "white"}}

        # Shows all offense types by default, shows specific offenses when user specifies
        for i in range(len(offenses_list)):
            if type_selection == offenses_list[i]:
                if i == 0:
                    crime_map = pdk.Deck(map_style="mapbox://styles/mapbox/dark-v11",
                                         initial_view_state=view_state,
                                         layers=layer_list,
                                         tooltip=tool_tip)
                else:
                    crime_map = pdk.Deck(map_style="mapbox://styles/mapbox/dark-v11",
                                         initial_view_state=view_state,
                                         layers=[layer_list[i - 1]],
                                         tooltip=tool_tip)

                st.pydeck_chart(crime_map)

    # Code for bar chart of crimes per district
    elif location_display == "Amount per District":
        # Finding number of offenses per district
        district_counts = [[x[1], df_crime["DISTRICT"].value_counts()[x[0]]] for x in regions_tuple()]

        names = [x[0] for x in district_counts]

        totals = [x[1] for x in district_counts]

        # Bar chart in streamlit
        x = np.arange(len(names))
        fig, ax = plt.subplots()
        plt.xticks(x, names, rotation=90)
        plt.xlabel("Districts")
        plt.ylabel("Number of Crimes Reported")
        plt.title("Number of Crimes Reported per District")
        bars = ax.bar(x, totals, width=0.5, color=np.random.rand(len(x), 3))
        ax.bar_label(bars)
        st.pyplot(fig)

# Code for time data
elif select_display == "Times of Day":
    # UI
    time_display = st.sidebar.radio("Which data would you like to access?", ["", "Histogram", "Pivot Table", "Crime Types per Time of Day"])

    if time_display == "Histogram":
        st.title("Histogram of Crimes over Time")

        # Histogram in streamlit
        fig, ax = plt.subplots()
        ax.hist(df_crime.HOUR, bins=[0, 3, 6, 9, 12, 15, 18, 21, 24], color="purple")
        plt.xticks([0, 3, 6, 9, 12, 15, 18, 21, 24])
        plt.xlabel("Time of Day (24 Hour)")
        plt.ylabel("Number of Crimes Reported")
        plt.title("Number of Crimes Reported per Time of Day")
        st.pyplot(fig)

    elif time_display == "Pivot Table":
        st.title("Number of Crimes per Hour per Day of Week")

        # Pivot table displaying number of crimes per hour of day and day of week
        sdf_pivot = df_crime[["HOUR", "DAY_OF_WEEK"]]

        time_pivot = pd.pivot_table(data=sdf_pivot, index=["DAY_OF_WEEK"], columns=["HOUR"], aggfunc=len, fill_value=0)
        st.write(time_pivot)

    elif time_display == "Crime Types per Time of Day":
        st.title("List of Crimes That Occurred Over Selected Time Frame")

        # Double slider for selecting desired range of times
        selected_times = st.sidebar.slider("What range of times would you like to access data for?", max_value=23,
                                           value=[0, 23])

        # Create sub-dataframe based on user input
        sdf_slider = df_crime[((df_crime.HOUR >= selected_times[0]) & (df_crime.HOUR <= selected_times[1]))][["HOUR", "OFFENSE_DESCRIPTION"]]

        times_offenses = []
        for y in sdf_slider.OFFENSE_DESCRIPTION:
            if y.lower().title().strip() not in times_offenses:
                times_offenses.append(y.lower().title().strip())

        # Display easier to read
        times_offenses_array = np.array(times_offenses)

        st.write(times_offenses_array)

# Code for type data
elif select_display == "Common Types":
    sdf_district_types = df_crime[["DISTRICT", "OFFENSE_DESCRIPTION"]]
    grouped_district_types = sdf_district_types.groupby(by=["DISTRICT"]).count()
    grouped_district_types.drop(["External"], axis=0, inplace=True)

    # Easier for me to extract needed data
    district_offenses = tuple(zip(df_districts["District Name"], grouped_district_types["OFFENSE_DESCRIPTION"]))

    names = [i[0] for i in district_offenses]
    vals = [i[1] for i in district_offenses]

    all_names = sorted(names)
    all_names.insert(0, "All")

    common_display = st.multiselect("Which districts would you like to access?", all_names, default="All")

    st.title("Pie Chart of Crime per District")

    # Default pie chart selection
    if "All" in common_display:
        pie_chart = px.pie(values=vals, names=names, title="Percentage of Crime by District")

    # Pie chart changes based on user input
    else:
        pie_vals = []
        for d in range(len(common_display)):
            for i in range(len(sorted(names))):
                if common_display[d] == sorted(names)[i]:
                    pie_vals.append(vals[i])

        pie_chart = px.pie(values=pie_vals, names=common_display, title="Percentage of Crime by District")

    st.plotly_chart(pie_chart)
