import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(page_title="Spreading Of Eyes Diseases",page_icon="🌍",layout="wide")

def fungsi_kategori_penyakit(df, kecamatan, tahun):
    filtered_df = df[(df['Kecamatan'] == kecamatan) & (df['Tahun'] == tahun)]
    kategori_penyakit = filtered_df.groupby(by=['Kecamatan', 'block_code']).agg({
        'block_code': 'count'
    }).rename(columns={"block_code": "count"}).reset_index()
    return kategori_penyakit

def fungsi_diagnosis_primer(df,kecamatan,tahun):
    filtered_df = df[(df['Kecamatan'] == kecamatan) & (df['Tahun'] == tahun)]
    diagnosis_penyakit = filtered_df.groupby(by=['Kecamatan','Diagnosis Primer']).agg({
        'Diagnosis Primer' : 'count'
    }).rename(columns={"Diagnosis Primer": "count"}).reset_index()
    top_10_diagnosis = diagnosis_penyakit.sort_values(by='count',ascending=False).head(10)
    return top_10_diagnosis

def fungsi_penyebaran_tahunan(df, kecamatan, tahun):
    filtered_df = df[(df['Kecamatan'] == kecamatan) & (df['Tahun'] == tahun)]
    month_names = [
        'Januari', 'Februari', 'Maret', 'April', 
        'Mei', 'Juni', 'Juli', 'Agustus', 
        'September', 'Oktober', 'November', 'Desember'
    ]
    filtered_df['Nama_Bulan'] = pd.Categorical(filtered_df['Nama_Bulan'], categories=month_names, ordered=True)
    penyebaran = filtered_df.groupby(by=['Nama_Bulan', 'total_pasien']).agg({
        'total_pasien': 'count'
    }).rename(columns={"total_pasien": "count"}).reset_index()
    penyebaran = penyebaran.sort_values(by='Nama_Bulan').reset_index(drop=True)
    return penyebaran

# Load GeoJSON file
with open("dissolved.geojson") as f:
    geojson_data = json.load(f)

# Load the existing dataset
dataset = pd.read_csv("All_data_mata.csv")
dataset['block_code'] = dataset['block_code'].str.replace("Disorders of", " ",regex=False).str.strip()

# File uploader to allow users to upload new dataWS
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    new_data = pd.read_csv(uploaded_file)
    dataset = pd.concat([dataset, new_data], ignore_index=True)
    st.sidebar.success("Data successfully uploaded and added to the existing dataset!")

# Add "All" option to kecamatan selection
options_kecamatan = ["All"] + list(dataset['Kecamatan'].unique())
options_tahun = dataset['Tahun'].unique()

# Title
st.title("Dashboard Penyebaran Penyakit Mata di Kabupaten Pangandaran")

# Select boxes for filters
selected_option_kecamatan = st.selectbox('Pilih Opsi Kecamatan:', options_kecamatan)
selected_option_tahun = st.selectbox('Pilih Opsi Tahun:', options_tahun)

# Apply filters to the dataset for the map
if selected_option_kecamatan == "All":
    filtered_map_dataset = dataset[dataset['Tahun'] == selected_option_tahun]
else:
    filtered_map_dataset = dataset[(dataset['Kecamatan'] == selected_option_kecamatan) & (dataset['Tahun'] == selected_option_tahun)]

# maps spreading eyes disease with filters
fig_choropleth = px.choropleth_mapbox(
    filtered_map_dataset, 
    geojson=geojson_data, 
    locations='Kecamatan', 
    color='cluster',
    featureidkey="properties.WADMKC",
    mapbox_style="open-street-map",
    center={"lat": filtered_map_dataset['Lat'].mean(), "lon": filtered_map_dataset['Long'].mean()},
    zoom=9,
    hover_data=["total_pasien"]
)

fig_choropleth.update_layout(
    height=600,
    margin={"r":0,"t":0,"l":0,"b":0}
)

st.plotly_chart(fig_choropleth, use_container_width=True)

# Ensure other visualizations are filtered by selected kecamatan (excluding "All" logic)
if selected_option_kecamatan != "All":
    kategori_penyakit_mata = fungsi_kategori_penyakit(dataset, selected_option_kecamatan, selected_option_tahun)
    top_10_diagnosis = fungsi_diagnosis_primer(dataset, selected_option_kecamatan, selected_option_tahun)
    waktu_penyebaran = fungsi_penyebaran_tahunan(dataset, selected_option_kecamatan, selected_option_tahun)

    kategori_penyakit = px.line(kategori_penyakit_mata, x=kategori_penyakit_mata['block_code'], y=kategori_penyakit_mata['count'], title=f"Kategori Penyakit Mata di Kecamatan {selected_option_kecamatan}")
    fig_business = px.bar(top_10_diagnosis, x=top_10_diagnosis['Diagnosis Primer'], y=top_10_diagnosis['count'], title=f"10 Diagnosis Penyakit Mata tertinggi di Kecamatan {selected_option_kecamatan}")
    fig_region = px.bar(waktu_penyebaran, x=waktu_penyebaran['Nama_Bulan'], y=waktu_penyebaran['count'], title=f"Time Series Penyakit Mata Di Kecamatan {selected_option_kecamatan} pada tahun {selected_option_tahun}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(kategori_penyakit, use_container_width=True)

    with col2:
        st.plotly_chart(fig_business, use_container_width=True)

    with col3:
        st.plotly_chart(fig_region, use_container_width=True)

st.caption("Copyright by Ferian Ardiansa Junardi")
