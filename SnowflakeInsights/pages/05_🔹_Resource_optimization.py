import streamlit as st

st.set_page_config(
    page_title="Resource Optimization", page_icon="🔹", layout="wide"
)

from utils import charts, gui, processing
#from utils import snowflake_connector as sf
from utils import sql as sql
import pandas as pd
import functions as fn
import altair as alt
import plotly.express as px
from datetime import date,timedelta,datetime
import pytz
from st_aggrid import AgGrid,GridUpdateMode,DataReturnMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from typing import Tuple

st.markdown("<h1 style='text-align: center; color: black;padding: 1% 1% 1% 1%;background-color: #a2d5f2;'>Resource Optimization</h1>", unsafe_allow_html=True)
style="""
.css-81oif8{
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



def main():
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

                def date_selection(key) -> Tuple[datetime.date, datetime.date]:
                    """Adds a date selector with a few different options."""

                    date_range = st.selectbox(
                        "Date range",
                        options=[
                            "Last 7 days",
                            "Last 28 days",
                            "Last 3 months"
                        ],
                        index=0,
                        key=key,
                    )

                    date_to = date.today()
                    if date_range == "Last 7 days":
                        date_from = date_to - timedelta(days=7)
                    elif date_range == "Last 28 days":
                        date_from = date_to - timedelta(days=28)
                    else:
                        date_from = date_to - timedelta(weeks=12)

                    st.caption(f"Your selection is from **{date_from}** to **{date_to}**")

                    return date_from, date_to
                
                tab1,tab2,tab3=st.tabs(["Setup & Configuration","Billing Metrics","Performance"])
                with tab1:              
                    Option_list=["Idle Roles","Idle Users","Idle Warehouses","Users Never Logged In","Warehouses Without Auto-Resume","Warehouses Without Auto-Suspend",
                                "Warehouses With Long Suspension","Warehouses Without Resource Monitors"]
                    sel_opt=st.selectbox("Select Option",Option_list,key='op1')
                    if sel_opt == "Warehouses Without Auto-Resume":
                        # WAREHOUSE=sql.WAREHOUSE
                        # df_warehouse=fn.get_model_run_date(WAREHOUSE)
                        # df_setup= fn.sql_to_dataframe(sql.WAREHOUSE_WO_AUTO_RESUME) 
                        df_setup=df_warehouse[df_warehouse["auto_resume"]=='false'][["name","size"]] 
                        
                    elif sel_opt == "Warehouses Without Auto-Suspend":
                        # WAREHOUSE=sql.WAREHOUSE
                        # df_warehouse=fn.get_model_run_date(WAREHOUSE)
                        # df_setup = fn.sql_to_dataframe(sql.WAREHOUSE_WO_AUTO_SUSPEND)
                        df_warehouse["auto_suspend"].fillna(0,inplace=True)
                        df_setup=df_warehouse[df_warehouse["auto_suspend"]==0][["name","size"]]
                        
                    elif sel_opt == "Warehouses With Long Suspension":
                        # WAREHOUSE=sql.WAREHOUSE
                        # df_warehouse=fn.get_model_run_date(WAREHOUSE)
                        #df_setup = fn.sql_to_dataframe(sql.WAREHOUSE_WI_LONG_SUSPENSION)
                        df_setup=df_warehouse[df_warehouse["auto_suspend"]>= 3600][["name","size"]]
                        
                    elif sel_opt == "Warehouses Without Resource Monitors":
                        # WAREHOUSE=sql.WAREHOUSE
                        # df_warehouse=fn.get_model_run_date(WAREHOUSE)
                        # df_setup = fn.sql_to_dataframe(sql.WAREHOUSE_WO_RESOURCE_MONITOR)
                        df_setup=df_warehouse[df_warehouse["resource_monitor"]=='null'][["name","size"]]
                        
                    elif sel_opt == "Idle Users":
                        date_from, date_to = date_selection('d1')
                        df_setup = fn.sql_to_dataframe(sql.IDLE_USERS.format(
                            date_from=date_from))
                        
                    elif sel_opt == "Users Never Logged In":
                        date_from, date_to = date_selection('d2')
                        df_setup = fn.sql_to_dataframe(sql.USERS_NEVER_LOGGED_IN.format(
                            date_from=date_from,
                            date_to=date_to))
                        
                    elif sel_opt == "Idle Roles":
                        date_from, date_to = date_selection('d3')
                        df_setup = fn.sql_to_dataframe(sql.IDLE_ROLES.format(
                            date_from=date_from,
                            date_to=date_to))
                        
                    else:
                        date_from, date_to = date_selection('d4')
                        # WAREHOUSE=sql.WAREHOUSE
                        # df_warehouse=fn.get_model_run_date(WAREHOUSE)
                        df_setup = fn.sql_to_dataframe(sql.IDLE_WAREHOUSES.format(
                            date_from=date_from,
                            date_to=date_to))
                        df_setup=df_warehouse[~df_warehouse.name.isin(df_setup["WAREHOUSE_NAME"])]

                    if df_setup.empty:
                        st.write("No data found")
                    else:
                        st.write("")
                        gd = GridOptionsBuilder.from_dataframe(df_setup)
                        gd.configure_pagination(enabled=True)
                        gd.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True)
                        gridoptions = gd.build()

                        res=AgGrid(df_setup,gridOptions=gridoptions,
                                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                                        height=250,
                                        theme='alpine')
                        sel_rows = res['selected_rows']
                        if sel_rows:
                            # log_inf.write("")
                            df_selected_rows = pd.DataFrame(sel_rows)
                            csv = df_selected_rows.to_csv().encode('utf-8')

                            st.download_button(
                                label="Download data as CSV",
                                data=csv,
                                file_name=sel_opt+'.csv',
                                mime='text/csv',
                            ) 
                with tab2:
                    billing_metrics=[#"Average Cost Per Query",
                    "AutoClustering Cost History","Materialized Views Cost History","Most Expensive Queries",
                    "Replication Cost History","Search Optimization Cost History","Snowpipe Cost History"]
                    
                    sel_metrics=st.selectbox("Select Option",billing_metrics,key='op2')
                    if sel_metrics == 'Most Expensive Queries':
                        date_from, date_to = date_selection('d5')
                        df_billing = fn.sql_to_dataframe(sql.MOST_EXPENSIVE_QUERY.format(
                            date_from=date_from,
                            date_to=date_to))

                    # elif sel_metrics == 'Average Cost Per Query':
                    #     df_billing = fn.sql_to_dataframe(sql.AVERAGE_COST_PER_QUERY.format(
                            # date_from=date_from,
                            # date_to=date_to))

                    elif sel_metrics == 'AutoClustering Cost History':
                        date_from, date_to = date_selection('d6')
                        df_billing = fn.sql_to_dataframe(sql.AUTOCLUSTERING_COST_HISTORY.format(
                            date_from=date_from,
                            date_to=date_to))

                    elif sel_metrics == 'Materialized Views Cost History':
                        date_from, date_to = date_selection('d7')
                        df_billing = fn.sql_to_dataframe(sql.MATERIALIZED_VIEWS_COST_HISTORY.format(
                            date_from=date_from,
                            date_to=date_to))

                    elif sel_metrics == 'Search Optimization Cost History':
                        date_from, date_to = date_selection('d8')
                        df_billing = fn.sql_to_dataframe(sql.SEARCH_OPTIMIZATION_COST_HISTORY.format(
                            date_from=date_from,
                            date_to=date_to))

                    elif sel_metrics == 'Snowpipe Cost History':
                        date_from, date_to = date_selection('d9')
                        df_billing = fn.sql_to_dataframe(sql.SNOWPIPE_COST_HISTORY.format(
                            date_from=date_from,
                            date_to=date_to))
                    else:
                        date_from, date_to = date_selection('d10')
                        df_billing = fn.sql_to_dataframe(sql.REPLICATION_COST_HISTORY.format(
                            date_from=date_from,
                            date_to=date_to))

                    if df_billing.empty:
                        st.write("No data found")
                    else:
                        st.write("")
                        gb = GridOptionsBuilder.from_dataframe(df_billing)
                        gb.configure_pagination(enabled=True)
                        gb.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True)
                        gridoptions = gb.build()

                        result=AgGrid(df_billing,gridOptions=gridoptions,
                                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                                        height=300,
                                        theme='alpine')
                        sel_result = result['selected_rows']
                        if sel_result:
                            # log_inf.write("")
                            df_selected_result = pd.DataFrame(sel_result)
                            csv = df_selected_result.to_csv().encode('utf-8')

                            st.download_button(
                                label="Download data as CSV",
                                data=csv,
                                file_name=sel_metrics+'.csv',
                                mime='text/csv',
                            ) 
                with tab3:
                    performance_opt=["Data Ingest With Snowpipe","Full Table Scans","Heavy Scanners",
                                     "Top 10 Spillers Remote","Warehouse Cache Usage"]
                    sel_perf=st.selectbox("Select Option",performance_opt,key='op3')
                    if sel_perf == 'Data Ingest With Snowpipe':
                        df_performance = fn.sql_to_dataframe(sql.DATA_INGEST_WI_SNOWPIPE)

                    elif sel_perf == 'Full Table Scans':
                        date_from, date_to = date_selection('d11')
                        df_full_table_scan = fn.sql_to_dataframe(sql.FULL_TABLE_SCANS.format(
                            date_from=date_from,
                            date_to=date_to))
                        col1,col2,col3=st.columns([3,2,2])
                        with col2:
                            format1 = st.radio('Choose a Visual',('Graph form', 'Tabular form'),horizontal=True,key='rb1')
                        if format1 == 'Graph form':
                            fig = px.bar(df_full_table_scan, x='USER_NAME', y='COUNT_OF_QUERIES')
                            fig.update_layout(xaxis_title='USERNAME',yaxis_title='QUERIES COUNT',width=1400,height=500)
                            st.write(fig)
                        else:
                            dl1,dl2=st.columns([6,1])
                            df_full_table_scan["COUNT_OF_QUERIES"]=df_full_table_scan["COUNT_OF_QUERIES"].astype(str)
                            csv=df_full_table_scan.to_csv().encode('utf-8')
                            with dl2:st.download_button(label="Download Table",data=csv,file_name='Full Table Scans.csv',mime='text/csv')
                            st.table(df_full_table_scan.head(20))

                    elif sel_perf == 'Heavy Scanners':
                        date_from, date_to = date_selection('d12')
                        df_heavy_scanners = fn.sql_to_dataframe(sql.HEAVY_SCANNERS.format(
                            date_from=date_from,
                            date_to=date_to))
                        col1,col2,col3=st.columns([3,2,2])
                        with col2:
                            format1 = st.radio('Choose a Visual',('Graph form', 'Tabular form'),horizontal=True,key='rb2')
                        if format1 == 'Graph form':
                            fig = px.bar(df_heavy_scanners, x='USER_NAME', y='AVG_PCT_SCANNED',color="WAREHOUSE_NAME")
                            fig.update_layout(xaxis_title='USERNAME',yaxis_title='AVG. PERCENTAGE SCANNED',width=1400,height=500)
                            st.write(fig)
                        else:
                            dl1,dl2=st.columns([6,1])
                            df_heavy_scanners["AVG_PCT_SCANNED"]=df_heavy_scanners["AVG_PCT_SCANNED"].astype(str)
                            csv=df_heavy_scanners.to_csv().encode('utf-8')
                            with dl2:st.download_button(label="Download Table",data=csv,file_name='Heavy Scanners.csv',mime='text/csv')
                            st.table(df_heavy_scanners.head(20))

                    elif sel_perf == 'Top 10 Spillers Remote':
                        date_from, date_to = date_selection('d13')
                        df_performance = fn.sql_to_dataframe(sql.TOP_10_SPILLERS_REMOTE.format(
                            date_from=date_from,
                            date_to=date_to))
                    else:
                        date_from, date_to = date_selection('d14')
                        df_wh_cache_usg = fn.sql_to_dataframe(sql.WAREHOUSE_CACHE_USAGE.format(
                            date_from=date_from,
                            date_to=date_to))
                        col1,col2,col3=st.columns([3,2,2])
                        with col2:
                            format1 = st.radio('Choose a Visual',('Graph form', 'Tabular form'),horizontal=True,key='rb2')
                        if format1 == 'Graph form':
                            fig = px.bar(df_wh_cache_usg, x='WAREHOUSE_NAME', y='MB_SCANNED',hover_data=['QUERY_COUNT','MB_SCANNED_FROM_CACHE','PERCENT_SCANNED_FROM_CACHE'])
                            fig.update_layout(xaxis_title='WAREHOUSE NAME',yaxis_title='MB SCANNED',width=1400,height=500)
                            st.write(fig)
                        else:
                            dl1,dl2=st.columns([6,1])
                            csv=df_wh_cache_usg.to_csv().encode('utf-8')
                            with dl2:st.download_button(label="Download Table",data=csv,file_name='Warehouse Cache Usage.csv',mime='text/csv')
                            st.table(df_wh_cache_usg.head(20))
                    if sel_perf not in ['Full Table Scans','Heavy Scanners','Warehouse Cache Usage']:
                        if df_performance.empty:
                            st.write("No data found")
                        else:
                            st.write("")
                            grd = GridOptionsBuilder.from_dataframe(df_performance)
                            grd.configure_pagination(enabled=True)
                            grd.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True)
                            gridoptions = grd.build()

                            response=AgGrid(df_performance,gridOptions=gridoptions,
                                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                                            height=300,
                                            theme='alpine')
                            sel_response = response['selected_rows']
                            if sel_response:
                                # log_inf.write("")
                                df_selected_response = pd.DataFrame(sel_response)
                                csv = df_selected_response.to_csv().encode('utf-8')

                                st.download_button(
                                    label="Download data as CSV",
                                    data=csv,
                                    file_name=sel_perf+'.csv',
                                    mime='text/csv',
                                ) 

            else:
                st.warning("Please login to access this page") 
        else:
            st.warning("Please login to access this page")    
    except AttributeError:
        st.warning("Please login to access this page")

if __name__ == "__main__":
    main()