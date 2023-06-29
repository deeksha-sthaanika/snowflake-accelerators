#from turtle import onclick
import streamlit as st
st.set_page_config(
    page_title="Snowatch App - Table Catalog", page_icon="🔹", layout="wide"
)
from typing import Any, Dict
from snowflake.connector import connect
from snowflake.connector.connection import SnowflakeConnection
import pandas as pd
import functions as fn
from utils import sql as sql
from st_aggrid import AgGrid,GridUpdateMode,DataReturnMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.markdown("<h1 style='text-align: center; color: black;padding: 1% 1% 1% 1%;background-color: #a2d5f2;'>Table Catalog</h1>", unsafe_allow_html=True)

style="""
.css-184tjsw p{
font-weight:bold
}
.js-plotly-plot .plotly, .js-plotly-plot .plotly div {
font-weight:bold
}
.css-163ttbj
{
    background-color:#cae7f7
}
.css-1hverof:hover,
{
   background-color:#FED8B1 
}
/*logout */
.css-zrs5io
{
   background-color:#F06055;
   color:white; 
}
.css-l6i7ys
{
  background-color:#1a98d7;
   color:white;  
}
.css-1053j7q:focus:(:active) {
  background-color:#5EC5F7;
   color:white;

"""
# div.stButton > button:first-child{
#  background-color:#28B1F5;
#    color:white;   
# }
st.markdown(f"<style>{style}</style>",unsafe_allow_html=True)
footer="""<style>.footer {
position: fixed;
left: 50;
bottom: 0;
width: 100%;
background-color: white;
color: grey;
text-align: left;
}
</style><div class="footer"><p>Snowatch</p></div>"""
st.markdown(footer,unsafe_allow_html=True)
st.markdown("""
<style>div.stButton > button:hover {
    background-color: #28B1F5;
    color:white;
    }
div.stButton > button:focus {
    background-color:#E0FFFF;
    color:white;
    }
div.stButton > button:active {
    background-color: #E0FFFF;
    color:white;
    }
</style>""", unsafe_allow_html=True)
st.markdown("""
<style>
div[data-testid="metric-container"] {
   background-color: rgba(219,226,233,0.8);
   border: 1px solid rgba(28, 131, 225, 0.1);
   padding: 10% 5% 5% 10%;
   border-radius: 25px;
   color: rgb(30, 103, 119);
   width: 180px;
   height: 110px;
   overflow-wrap: break-word;
}
/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: rgba(35,86,131);
   font-size: 16px;
   font-weight:bold
}
div[data-testid="metric-container"] > div[data-testid="stMetricValue"] > div {
   font-size: 19px;
   color:rgba(28, 34, 80)
}
</style>
"""
, unsafe_allow_html=True)

try:
    if st.session_state.success_param:
        logout_btn=st.sidebar.button("Logout")
        if logout_btn:
            st.write("Successfully Logged out "+st.session_state.usrname)
            # st.session_state.clear()
            st.session_state.success_param=False
            st.session_state.usrname=''
            st.session_state.password_ip=''
            st.session_state.account=''
        
        if st.session_state.success_param:
            df_role = fn.sql_to_dataframe(sql.ROLE)
            if 'role' not in st.session_state:
                role=st.sidebar.selectbox("Select Role",df_role["role"],key='role')
            else:    
                role=st.sidebar.selectbox("Select Role",df_role["role"],index=list(df_role["role"]).index(st.session_state.role),key='role')
            
            df_warehouse = fn.sql_to_dataframe(sql.WAREHOUSE)
            wh=st.sidebar.selectbox("Select Warehouse",df_warehouse["name"],key='s2')

            df = fn.sql_to_dataframe(sql.USE_ROLE.format(role=role))

            df = fn.sql_to_dataframe(sql.USE_WAREHOUSE.format(wh=wh))

            df_total_dbs= fn.sql_to_dataframe(sql.TOTAL_DBS)
            df_total_tables= fn.sql_to_dataframe(sql.TOTAL_TABLES)
            #df_failed_login= fn.sql_to_dataframe(sql.FAILED_LOGIN_ATTEMPTS)

            #col1,col2,col3,col4,col5=st.columns([4,2,2,2,4])
            col1,col2,col3,col4=st.columns([4,2,2,4])
            col2.metric("#Databases",df_total_dbs.iloc[0][0])
            col3.metric("#Tables",df_total_tables.iloc[0][0])
            #col4.metric("Failed Login Attempts (%)",round(df_failed_login.iloc[0][0],2))

            df=fn.sql_to_dataframe(sql.TABLE_CATALOG)

            catalog_inf=st.empty()
            catalog_inf.markdown(
                    "<h6 style='text-align: center; color: midnightblue;'>Select checkbox to download",
                    unsafe_allow_html=True)
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(enabled=True)
            gb.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True)
            gridoptions = gb.build()

            response=AgGrid(df,gridOptions=gridoptions,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            height=500,
                            theme='alpine')
            sel_rows = response['selected_rows']
            if sel_rows:
                catalog_inf.write("")
                df = pd.DataFrame(sel_rows)
                csv = df[["TABLE_ID","TABLE_CATALOG","CREATED","TABLE_NAME","TABLE_SCHEMA","TABLE_OWNER","TABLE_TYPE",
                          "IS_TRANSIENT","CLUSTERING_KEY","ROW_COUNT","BYTES","RETENTION_TIME","LAST_ALTERED",
                          "AUTO_CLUSTERING_ON","COMMENT","COLUMN_COUNT"]].to_csv().encode('utf-8')

                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='Table Catalog.csv',
                    mime='text/csv',
                )  
        else:
            st.warning("Please login to access this page") 
    else:
        st.warning("Please login to access this page")
except AttributeError:
    st.warning("Please login to access this page")