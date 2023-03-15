import snowflake.connector
from snowflake.snowpark.session import Session

import pandas as pd
import streamlit as st
from snowflake.connector import connect
from snowflake.connector.connection import SnowflakeConnection
from snowflake.connector.pandas_tools import write_pandas
import numpy as np
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import time
import sys
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Any, Dict
# from utils import snowflake_connector as sf
from utils import sql,gui
import datetime


@st.cache_resource(show_spinner=False)
def get_connector(
    secrets_key: str = "snowflake",
    input_params: Dict[str, Any] = None,
    use_browser=True,
) -> SnowflakeConnection:
    # Default params
    params: Dict[str, Any] = {
        **st.secrets[secrets_key],
        "client_session_keep_alive": True,
        "client_store_temporary_credential": True,
    }

    # Override default params with input params
    if input_params:
        for key in input_params.keys():
            params[key] = input_params[key]

    # This will open a tab in your browser and sign you in
    if use_browser:
        params["authenticator"] = "externalbrowser"

    connector = connect(**params)
    return connector


@st.cache_data(ttl=10,show_spinner=False)#ttl=60*60,
def sql_to_dataframe(sql_query: str) -> pd.DataFrame:
    snowflake_connector = get_connector(   
    secrets_key="sf_usage_app",  
    input_params={'user':st.session_state.usrname,'password':st.session_state.password_ip,'account':st.session_state.account},#,'warehouse':st.session_state.whname,'role':st.session_state.role
    use_browser=False,)
    data = pd.read_sql(
        sql_query,snowflake_connector
    )
    # st.write(st.session_state)
    return data

@st.cache_data(ttl=10,show_spinner=False)
def get_queries_data(
    date_from: datetime.date,
    date_to: datetime.date,
):
    queries_data = sql_to_dataframe(
        sql.QUERIES_QUERY.format(
            date_from=date_from,
            date_to=date_to,
        )
    )
    queries_data["DURATION_SECS"] = round(
        (queries_data.TOTAL_ELAPSED_TIME) / 1000
    )
    queries_data["DURATION_SECS_PP"] = queries_data.DURATION_SECS.apply(
        gui.pretty_print_seconds
    )
    queries_data["QUERY_TEXT_PP"] = queries_data.QUERY_TEXT.apply(
        gui.pretty_print_sql_query
    )
    return queries_data

    





