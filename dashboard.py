import streamlit as st
import pandas as pd
import plotly.express as px

# Generate dummy data
business_types = ['Apartment', 'Farming', 'Office Bldg', 'Retail', 'Hospitality', 'Manufacturing', 'Organization', 'Service', 'Education', 'Medical', 'Recreation', 'Construction']
investments_by_type = [150, 80, 120, 40, 60, 30, 70, 20, 10, 15, 25, 50]
regions = ['Dodoma', 'Kigoma', 'Dar es Salaam', 'Mwanza', 'Arusha', 'Kilimanjaro', 'Iringa']
ratings = [50, 18.7, 17.1, 5, 3, 4, 2.2]
st.set_page_config(page_title="Dashboard",page_icon="🌍",layout="wide")

def fungsi_kategori_penyakit(df, kecamatan, tahun):
    # Filter data berdasarkan kecamatan dan tahun
    filtered_df = df[(df['Kecamatan'] == kecamatan) & (df['Tahun'] == tahun)]
    
    # Mengelompokkan data berdasarkan Kecamatan dan block_code
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
    # Filter data berdasarkan kecamatan dan tahun
    filtered_df = df[(df['Kecamatan'] == kecamatan) & (df['Tahun'] == tahun)]
    
    # Daftar nama bulan berurutan
    month_names = [
        'Januari', 'Februari', 'Maret', 'April', 
        'Mei', 'Juni', 'Juli', 'Agustus', 
        'September', 'Oktober', 'November', 'Desember'
    ]
    
    # Mengubah kolom Nama_Bulan menjadi kategori dengan urutan yang benar
    filtered_df['Nama_Bulan'] = pd.Categorical(filtered_df['Nama_Bulan'], categories=month_names, ordered=True)
    
    # Mengelompokkan data berdasarkan Nama_Bulan dan total_pasien
    penyebaran = filtered_df.groupby(by=['Nama_Bulan', 'total_pasien']).agg({
        'total_pasien': 'count'
    }).rename(columns={"total_pasien": "count"}).reset_index()
    
    # Mengurutkan berdasarkan Nama_Bulan
    penyebaran = penyebaran.sort_values(by='Nama_Bulan').reset_index(drop=True)
    
    return penyebaran





dataset = pd.read_csv("all_data_mata.csv")
dataset['block_code'] = dataset['block_code'].str.replace("Disorders of", " ",regex=False).str.strip()

options_kecamatan = dataset['Kecamatan']
options_tahun = dataset['Tahun'].unique()





# Membuat select box

# Title
st.title("Penyebaran Penyakit Mata di Kabupaten Pangandaran")
selected_option_kecamatan = st.selectbox('Pilih Opsi Kecamatan:', options_kecamatan)
selected_option_tahun = st.selectbox('Pilih Opsi Tahun:', options_tahun)


kategori_penyakit_mata = fungsi_kategori_penyakit (dataset,selected_option_kecamatan,selected_option_tahun)
top_10_diagnosis = fungsi_diagnosis_primer (dataset,selected_option_kecamatan,selected_option_tahun) 
waktu_penyebaran = fungsi_penyebaran_tahunan(dataset,selected_option_kecamatan,selected_option_tahun)

kategori_penyakit = px.line(kategori_penyakit_mata, x=kategori_penyakit_mata['block_code'], y=kategori_penyakit_mata['count'], title=f"Penyebaran penyakit di Kecamatan {selected_option_kecamatan}")
# Create bar chart (Investment by Business Type)
fig_business = px.bar(top_10_diagnosis, x=top_10_diagnosis['Diagnosis Primer'], y=top_10_diagnosis['count'], title="")

# Create pie chart (Ratings by Regions)
fig_region = px.bar(waktu_penyebaran, x=waktu_penyebaran['Nama_Bulan'], y=waktu_penyebaran['count'], title="")

# Layout the visualizations in a single row
col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(kategori_penyakit, use_container_width=True)

with col2:
    st.plotly_chart(fig_business, use_container_width=True)

with col3:
    st.plotly_chart(fig_region, use_container_width=True)
