# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 18:35:35 2022

@author: deeksha.bs
"""
import snowflake.connector
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
# from numerize import numerize
import time
import sys
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Any, Dict
from utils import sql

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
def dataframe_sql_to(df,db,schema,table_name,usrname):
    snowflake_connector = get_connector(   
    secrets_key="sf_usage_app",  
    input_params={'user':st.session_state.usrname,'password':st.session_state.password_ip,'account':st.session_state.account},#,'warehouse':st.session_state.whname,'role':st.session_state.role
    use_browser=False,)
    # data = pd.read_sql(
    #     sql_query,snowflake_connector
    # )
    # df.to_sql(table_name, snow_eng, index=False, method=pd_writer)
    success, num_chunks, num_rows, output = write_pandas(
        conn=snowflake_connector,
        df=df,
        table_name=table_name,
        database=db,
        schema=schema
    )


@st.cache_data(ttl=10,show_spinner=False)#ttl=60*60,
def sql_to_dataframe(sql_query: str,usrname) -> pd.DataFrame:
    snowflake_connector = get_connector(   
    secrets_key="sf_usage_app",  
    input_params={'user':st.session_state.usrname,'password':st.session_state.password_ip,'account':st.session_state.account},#,'warehouse':st.session_state.whname,'role':st.session_state.role
    use_browser=False,)
    data = pd.read_sql(
        sql_query,snowflake_connector
    )
    # st.write(st.session_state)
    return data

@st.cache_data(ttl=10,show_spinner=False)#ttl=60*60,
def get_query_data(query,usrname):
    df = sql_to_dataframe(query,usrname)
    return df

# @st.cache_data(ttl=60*60,show_spinner=False)#ttl=60*60,
# def get_model_run_date(query,usrname):
#     df = sql_to_dataframe(query,usrname)
#     return df

# @st.cache_data(ttl=60*60,show_spinner=False)#ttl=1,
# def get_query_2(query,arg2,usrname):
#     df = sql_to_dataframe(
#         query.format(arg2=arg2),st.session_state.usrname)
#     return df

# @st.cache_data(ttl=60*60,show_spinner=False)#ttl=1,
# def get_query_3(query,arg2,arg3,usrname):
#     df = sql_to_dataframe(
#         query.format(arg2=arg2,arg3=arg3),st.session_state.usrname)
#     return df

# @st.cache_data(ttl=60*60,show_spinner=False)#ttl=1,
# def get_query_4(query,arg2,arg3,arg4,usrname):
#     df = sql_to_dataframe(
#         query.format(arg2=arg2,arg3=arg3,arg4=arg4),st.session_state.usrname)
#     return df

@st.cache_resource(show_spinner=False)
def init_connection():
    return snowflake.connector.connect(
     **st.secrets["snowflake"], client_session_keep_alive=True
    ) 


@st.cache_data(ttl=60*60,show_spinner=False)
def proc_call(sql_query: str,usrname):
    snowflake_connector = get_connector(   
    secrets_key="sf_usage_app",  
    input_params={'user':st.session_state.usrname,'password':st.session_state.password_ip,'account':st.session_state.account},#,'warehouse':st.session_state.whname,'role':st.session_state.role
    use_browser=False,)
    cursor=snowflake_connector.cursor()
    cursor.execute_async(sql_query)

@st.cache_data(ttl=60*60,show_spinner=False)
def runquery(sql_query: str,usrname):
    snowflake_connector = get_connector(   
    secrets_key="sf_usage_app",  
    input_params={'user':st.session_state.usrname,'password':st.session_state.password_ip,'account':st.session_state.account},#,'warehouse':st.session_state.whname,'role':st.session_state.role
    use_browser=False,)
    cursor=snowflake_connector.cursor()
    cursor.execute(sql_query)
    return cursor.fetchall()

    





