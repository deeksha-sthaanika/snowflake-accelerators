import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
# import plotly.express as px # interactive charts 
import snowflake.connector
from utils import sql as sql
import functions as fn
import os
import pandas as pd 
import ydata_profiling as pp
from ydata_profiling import compare
# from pandas_profiling import ProfileReport
# from json2html import *
import json
from streamlit_pandas_profiling import st_profile_report
import streamlit.components.v1 as components
# from bs4 import BeautifulSoup

# with st.container():
#     cola,colb=st.columns([1,4])
#     with cola:
#         image1 = Image.open('Fractal-Logo-WithBL.png')
#         # st.image(image1,width=150)
#     with colb:
#         st.write("")
#         # st.markdown("<h3 style='text-align: left; color: #016299;padding: 0% 0% 0% 0%;font-size:34px'> | Speed Reliability Insights</h3>", unsafe_allow_html=True)
#     st.write("")
    # st.markdown("<h1 style='text-align: center; color: white;padding: 0% 0% 0% 0%;background-color: rgba(16,27,72);'>Network Condition</h1>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: black;padding: 1% 1% 1% 1%;background-color: #a2d5f2;'>Data Profiler</h1>", unsafe_allow_html=True)
#FCD374
footer="""<style>
.footer {
position: fixed;
left: 50;
bottom: 0;
width: 100%;
background-color: white;
color: grey;
text-align: left;
}
</style>
<div class="footer">
<p>SnowProcSQLite</p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)
st.markdown("""
<style>
div.stButton > button:hover,focus,active {
    background-color: #28B1F5;
    color:white;
    }
</style>""", unsafe_allow_html=True)
style="""
.css-81oif8{
font-weight:bold
}
/*sidebar*/
.css-163ttbj
{
    background-color:#cae7f7
}
/*logout */
.css-zrs5io
{
   background-color:#F06055;
   color:white; 
}
/*button*/
.css-l6i7ys
{
  background-color:#1a98d7;
   color:white;  
}

"""
# div.stButton > button:first-child{
#  background-color:#28B1F5;
#    color:white;   
# }
st.markdown(f"<style>{style}</style>",unsafe_allow_html=True)


# ### Page configuration- Use the full page instead of a narrow central column
####################### Data Card CSV ######################################

st.markdown("""
<style>
div[data-testid="metric-container"] {
   background-color: rgba(219,226,233,0.8);
   border: 1px solid rgba(28, 131, 225, 0.1);
   padding: 10% 10% 10% 10%;
   border-radius: 25px;
   color: rgb(30, 103, 119);
   width: 130px;
   height: 110px;
   overflow-wrap: break-word;
}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: rgba(35,86,131);
   font-size: 15px;
   font-weight:bold
}
div[data-testid="metric-container"] > div[data-testid="stMetricValue"] > div {
   font-size: 19px;
   color:rgba(28, 34, 80)
}
</style>
"""
, unsafe_allow_html=True)
style="""
thead tr th:first-child {display:none;}
tbody th {display:none;}
thead{
background-color:SkyBlue;
font-size: 20px;
font-weight:bold
}
tbody{
font-size: 19px;
font-weight:bold;
background-color:AliceBlue
}
.css-81oif8{
font-size: 17px;

}
.css-a51556{
    color:white
}

"""
st.markdown(f"<style>{style}</style>",unsafe_allow_html=True)
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
            ROLE=sql.ROLE
            df_role=fn.get_model_run_date(ROLE)
            if 'role' not in st.session_state:
                role=st.sidebar.selectbox("Select Role",df_role["role"],key='role')
            else:    
                role=st.sidebar.selectbox("Select Role",df_role["role"],index=list(df_role["role"]).index(st.session_state.role),key='role')
            
            WAREHOUSE=sql.WAREHOUSE
            df_warehouse=fn.get_model_run_date(WAREHOUSE)
            wh=st.sidebar.selectbox("Select Warehouse",df_warehouse["name"],key='s2')
            
            USE_ROLE=sql.USE_ROLE
            df=fn.get_query_2(USE_ROLE,role)
            
            USE_WAREHOUSE=sql.USE_WAREHOUSE
            df=fn.get_query_2(USE_WAREHOUSE,wh)

            TABLE=sql.TABLE
            df_table=fn.get_model_run_date(TABLE)

            df_table=df_table[df_table["owner"]!='']

            c1,c2,c3,c4=st.columns(4)

            db=c1.selectbox("Select Database",df_table["database_name"].unique(),key='s3')

            sch=c2.selectbox("Select Schema",df_table[df_table["database_name"]==db].schema_name.unique(),key='s4')

            table_sel=c3.selectbox("Select Table",df_table[(df_table["database_name"]==db) & (df_table["schema_name"]==sch)].name,key='s5')

            table_name=db+"."+sch+"."+table_sel

            COLUMNS=sql.COLUMNS
            df_cols=fn.get_query_4(COLUMNS,db,sch,table_sel)


            st.sidebar.markdown("<p style='margin-bottom: 15px;'><b>Select Columns to profile:</b></p>", unsafe_allow_html=True) 
            check_box=st.sidebar.empty()
            multi_select=st.sidebar.empty()
            select_all = check_box.checkbox("Select all",value=True)

            if select_all:
                cols_sel = multi_select.multiselect('Select Columns to profile:', ['All selected'], ['All selected'], disabled=True, label_visibility='collapsed',key='m1')
                cols_sel = list(df_cols["COLUMN_NAME"])
            else:
                cols_sel = st.sidebar.multiselect('Select Columns to profile:',df_cols,df_cols["COLUMN_NAME"].head(2), label_visibility='collapsed',key='m2')
                
            cols_sel_str='\''+ ','.join(map(str, cols_sel)) +'\''
            # st.write('"'+ '","'.join(map(str, cols_sel)) +'"')

            # st.write(cols_sel)

            sample_sel=c4.number_input("Enter Sample percentage",min_value=10.0,max_value=100.0)
            cols_sel_interaction=st.multiselect("select columns for interaction",cols_sel,cols_sel[0])
            # cols_sel_interaction='\''+ ','.join(map(str, cols_sel_interaction)) +'\''

            c11,c22,c33,c44=st.columns(4)
            sens=c11.checkbox("Show Sensitive")
            mini=c22.checkbox("Show Minimal")
            # comp=c33.checkbox("Compare the report with a different version") 
            # c44.empty()        

            if sens:
                sensitive=False
            else:
                sensitive=True
            if mini:
                minimal=True
            else:
                minimal=False
            # if comp:
            #     table_sel_comp=c44.selectbox("Select Table to compare",df_table[(df_table["database_name"]==db) & (df_table["schema_name"]==sch)].name,key='s6')
            #     table_name_comp=db+"."+sch+"."+table_sel_comp
            # else:
            #     c44.empty()


            # def profiling_data_with_pandas_py():
            #     SAMPLE=sql.SAMPLE
            #     df_sample =fn.get_query_3(SAMPLE,table_name,sample_sel)

            #     df_sample=df_sample[cols_sel]
            #     # st.write(df_sample)
            #     #res_df = snowpark_session.table(profile_table)	 
            #     #results_df_pd = res_df.to_pandas()
            #     if cols_sel_interaction:
            #         # profile = ProfileReport()
            #         # profile.config.interactions.targets = cols_sel

            #         # # Assigning a DataFrame and exporting to a file, triggering computation
            #         # profile.df_sample = df_sample
            #         # if samp:
            #         #     report = df_sample.profile_report(sensitive=sensitive,minimal=minimal)
            #         # else:
            #         #     report = df_sample.profile_report(samples=None,sensitive=sensitive,minimal=minimal)
            #         # if samp:
            #         if comp:
            #             table_sel_comp=c44.selectbox("Select Table to compare",df_table[(df_table["database_name"]==db) & (df_table["schema_name"]==sch)].name,key='s6')
            #             table_name_comp=db+"."+sch+"."+table_sel_comp

            #             SAMPLE=sql.SAMPLE
            #             df_sample_comp =fn.get_query_3(SAMPLE,table_name_comp,sample_sel)
            #             df_sample_comp=df_sample_comp[cols_sel]

            #             profile1 = pp.ProfileReport(df_sample,sensitive=sensitive,minimal=minimal)
            #             profile1.config.interactions.targets = cols_sel_interaction
            #             profile2=pp.ProfileReport(df_sample_comp,sensitive=sensitive,minimal=minimal)
            #             profile2.config.interactions.targets = cols_sel_interaction
            #             comparison_report = profile1.compare(profile2)
            #         else:
            #             c44.empty()
            #             comparison_report = pp.ProfileReport(df_sample,sensitive=sensitive,minimal=minimal)
            #             comparison_report.config.interactions.targets = cols_sel_interaction
            #         # else:
            #             # profile = pp.ProfileReport(df_sample,sensitive=sensitive,minimal=minimal)
                    

            #     # st.write(profile)
            #     st_profile_report(comparison_report)
                # profile.to_file("output.html")

            def profiling_data_with_pandas(): 
                # if comp:   
                #     PROFILE=sql.PROFILE_COMP.format(arg2=table_name_comp,arg3=sample_sel,arg4=cols_sel_str,arg5=cols_sel_interaction,arg6=sensitive,arg7=minimal,arg8=table_name_comp)
                # else:
                PROFILE=sql.PROFILE_SINGLE.format(arg2=table_name,arg3=sample_sel,arg4=cols_sel_str,arg5=cols_sel_interaction,arg6=sensitive,arg7=minimal)

                df_profile =fn.runquery(PROFILE)
                # st.write(df_profile)
                print("Total rows are:  ", len(df_profile))
                print("Printing each row")
                for row in df_profile:
                    print("html: ", row[0])
                #st.markdown(row[0], unsafe_allow_html=True)
                components.html(row[0],width=1400,height=1500,scrolling=True)

            
            # profiling_data_with_pandas_py()
            profiling_data_with_pandas()
        else:
            st.warning("Please login to access this page") 
    else:
        st.warning("Please login to access this page")
except AttributeError:
    st.warning("Please login to access this page")
