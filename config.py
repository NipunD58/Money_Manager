# config.py
import streamlit as st

MONGO_URI = st.secrets.get('MONGO_URI', 'MONGO_URI')
DATABASE_NAME = 'money_manager'
GOOGLE_API_KEY = st.secrets.get('GOOGLE_API_KEY')