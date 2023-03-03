import streamlit as st

st.set_page_config(
    page_title="Usage Insights app - About", page_icon="🤔", layout="centered"
)

from utils import gui

gui.icon("🤔")
st.title("About this app")

st.write(
    """
### How does this app work?

- Using [Streamlit](https://www.streamlit.io) and the [Snowflake Python
  connector](https://github.com/snowflakedb/snowflake-connector-python).


### Questions? Comments?

Please ask in the [Streamlit community](https://discuss.streamlit.io).
"""
)
