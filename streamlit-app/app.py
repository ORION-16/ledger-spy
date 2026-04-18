import streamlit as st
import pandas as pd

st.title("LedgerSpy 🧠")

file = st.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
    st.write("Preview of Data:")
    st.dataframe(df)