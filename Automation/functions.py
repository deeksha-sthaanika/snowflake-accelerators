# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 18:35:35 2022

@author: deeksha.bs
"""
import snowflake.connector
from snowflake.snowpark.session import Session

import pandas as pd
import streamlit as st
from snowflake.connector import connect
from snowflake.connector.connection import SnowflakeConnection
from snowflake.connector.pandas_tools import write_pandas
# from snowflake.connector.pandas_tools import pd_writer
# from snowflake.sqlalchemy import create_engine
# from types import *
# from sqlalchemy.dialects import registry
# from snowflake.snowpark.functions import avg, sum, col,lit
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
# from utils import snowflake_connector as sf



from utils import sql

# registry.register('snowflake', 'snowflake.sqlalchemy', 'dialect')
# st.session_state.password_ip=""
# st.session_state.usrname=""
# st.session_state.account=""

# @st.experimental_singleton(show_spinner=False)
# def create_session():
#     if "snowpark_session" not in st.session_state:
#         session = Session.builder.configs(st.secrets["sf_usage_app"]).create()
#         st.session_state['snowpark_session'] = session
#     else:
#         session = st.session_state['snowpark_session']
#     return session

# session=create_session()

# TIME_TO_LIVE = 60 * 60 * 6  # 6 hours caching

# st.write("importing function")
# st.write("Function state",st.session_state)
# Share the connector across all users connected to the app
# if st.session_state.usrname=='' or st.session_state.password_ip=='' or st.session_state.account=='':
#     st.session_state.usrname=' '
#     st.session_state.password_ip=' '
#     st.session_state.account=' '

@st.experimental_singleton(show_spinner=False)
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

# if st.session_state.usrname and st.session_state.password_ip and st.session_state.account:  
# snowflake_connector = get_connector(   
#     secrets_key="sf_usage_app",  
#     input_params={'user':st.session_state.usrname,'password':st.session_state.password_ip,'account':st.session_state.account},#,'warehouse':st.session_state.whname,'role':st.session_state.role
#     use_browser=False,)

# snow_eng=create_engine(f"snowflake://{st.session_state.usrname}:{st.session_state.password_ip}@{st.session_state.account}").connect()

@st.experimental_memo(ttl=60*60,show_spinner=False)#ttl=60*60,
def dataframe_sql_to(df,db,schema,table_name):
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


@st.experimental_memo(ttl=60*60,show_spinner=False)#ttl=60*60,
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

@st.experimental_memo(ttl=60*60,show_spinner=False)#ttl=60*60,
def get_model_run_date(query):
    df = sql_to_dataframe(query)
    return df

@st.experimental_memo(ttl=60*60,show_spinner=False)#ttl=1,
def get_query_2(query,arg2):
    df = sql_to_dataframe(
        query.format(arg2=arg2))
    return df

@st.experimental_memo(ttl=60*60,show_spinner=False)#ttl=1,
def get_query_3(query,arg2,arg3):
    df = sql_to_dataframe(
        query.format(arg2=arg2,arg3=arg3))
    return df

@st.experimental_memo(ttl=60*60,show_spinner=False)#ttl=1,
def get_query_4(query,arg2,arg3,arg4):
    df = sql_to_dataframe(
        query.format(arg2=arg2,arg3=arg3,arg4=arg4))
    return df

@st.experimental_singleton(show_spinner=False)
def init_connection():
    return snowflake.connector.connect(
     **st.secrets["snowflake"], client_session_keep_alive=True
    ) 


@st.experimental_memo(ttl=60*60,show_spinner=False)
def proc_call(sql_query: str):
    snowflake_connector = get_connector(   
    secrets_key="sf_usage_app",  
    input_params={'user':st.session_state.usrname,'password':st.session_state.password_ip,'account':st.session_state.account},#,'warehouse':st.session_state.whname,'role':st.session_state.role
    use_browser=False,)
    cursor=snowflake_connector.cursor()
    cursor.execute_async(sql_query)

@st.experimental_memo(ttl=60*60,show_spinner=False)
def runquery(sql_query: str):
    snowflake_connector = get_connector(   
    secrets_key="sf_usage_app",  
    input_params={'user':st.session_state.usrname,'password':st.session_state.password_ip,'account':st.session_state.account},#,'warehouse':st.session_state.whname,'role':st.session_state.role
    use_browser=False,)
    cursor=snowflake_connector.cursor()
    cursor.execute(sql_query)
    return cursor.fetchall()

    





