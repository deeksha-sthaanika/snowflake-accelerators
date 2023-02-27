import streamlit as st
st.set_page_config(page_title="Adhoc Jobs", page_icon="gear.png", layout="wide")
import pandas as pd
import os
# import altair as alt
# import numpy as np
# import plotly.graph_objects as go
# from plotly.validators.scatter.marker import SymbolValidator
# import plotly.figure_factory as ff
# import datetime as dt
# from dateutil.relativedelta import relativedelta # to add days or years
# from plotly.subplots import make_subplots
# import plotly.express as px
# from datetime import timedelta
# # from utils import snowflake_connector as sf
from utils import sql as sql
import functions as fn
import gzip
# # from numerize import numerize
from PIL import Image
from st_aggrid import AgGrid,GridUpdateMode,DataReturnMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
# import string
######################################################################################
with st.container():
    cola,colb=st.columns([1,4])
    with cola:
        image1 = Image.open('Fractal-Logo-WithBL.png')
        # st.image(image1,width=150)
    with colb:
        st.write("")
        # st.markdown("<h3 style='text-align: left; color: #016299;padding: 0% 0% 0% 0%;font-size:34px'> | Speed Reliability Insights</h3>", unsafe_allow_html=True)
    st.write("")
    # st.markdown("<h1 style='text-align: center; color: white;padding: 0% 0% 0% 0%;background-color: rgba(16,27,72);'>Network Condition</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: black;padding: 1% 1% 1% 1%;background-color: #a2d5f2;'>Adhoc Task Handler</h1>", unsafe_allow_html=True)
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
                     
            USE_DATABASE=sql.USE_DATABASE
            df=fn.get_model_run_date(USE_DATABASE)

            USE_SCHEMA_NAME=sql.USE_SCHEMA_NAME
            df=fn.get_model_run_date(USE_SCHEMA_NAME)

            tab1,tab3,tab2 = st.tabs(["RUN JOB","AUDIT JOB LOGS","STAGE JOB FILES"])
            with tab1:
                SCRIPT_NAME=sql.SCRIPT_NAME
                script_name=fn.get_model_run_date(SCRIPT_NAME)

                c1,c2,c3,c4=st.columns([2,2,1,1])
                with c2:
                    script_selected = st.selectbox('Select Script Name',script_name['SCRIPT_NAME'].unique(),key='s3')
                    script_sel='\''+ '\',\''.join(map(str, script_selected)) +'\''
                df_job_script=script_name[script_name["SCRIPT_NAME"]==script_selected]
                
                totrows= df_job_script.shape[0]
                sel_rows = pd.DataFrame(columns=["JOB_ID","SCRIPT_NAME","SEQ_ID","SQL_COMMAND","CONTINUE_ON_ERROR","IGNORE_SCRIPT"])
                gd = GridOptionsBuilder.from_dataframe(df_job_script)
                gd.configure_pagination(enabled=True)
                gd.configure_selection(selection_mode="multiple", use_checkbox=True,pre_selected_rows=[0],header_checkbox=True)
                gridoptions = gd.build()
                st.write("")
                response=AgGrid(df_job_script,gridOptions=gridoptions,
                                update_mode=GridUpdateMode.MODEL_CHANGED,
                                fit_columns_on_grid_load=True,
                                theme='alpine')
                sel_rows = response['selected_rows']
                #st.write(sel_rows)

                #df_sel_rows = pd.DataFrame(columns=["JOB_ID","SCRIPT_NAME","RUN_ID","SQL_COMMAND","CONTINUE_ON_ERROR","IGNORE_SCRIPT"])
                #st.dataframe(sel_rows)
                df_sel_rows = pd.DataFrame(sel_rows)
                if len(df_sel_rows)==0:
                    st.warning("Please select a row to edit")
                else:   
                    df_sel_rows["SEQ_ID"]=df_sel_rows["SEQ_ID"].astype(int)

                    if totrows == len(df_sel_rows["SEQ_ID"]):
                        runid_all=True
                        runid_sel=df_sel_rows["SEQ_ID"]
                    else:
                        runid_all=False
                        runid_sel=df_sel_rows["SEQ_ID"]
                
                execute=False
                execute_btn_prl=False
                execute_btn_sr=False

                c1, c2, c3, c4 = st.columns([4,1,1,4])
                sel_plc=c2.empty()
                if len(df_sel_rows)==1:
                    execute=sel_plc.button("Execute")
                else:
                    execute_btn_sr = sel_plc.button("Execute in series")
                    execute_btn_prl=c3.button("Execute in parallel")

                if execute_btn_sr or execute:
                    BATCH_ID_SEQ=sql.BATCH_ID_SEQ
                    df_batch_id=fn.get_model_run_date(BATCH_ID_SEQ)
                    batch_id=df_batch_id.iloc[0][0]
                    if runid_all:
                        STORED_PROC=sql.STORED_PROC
                        with st.spinner("Executing script in Snowflake"):
                            df=fn.get_query_3(STORED_PROC,script_selected,batch_id)
                            st.write("Executed "+script_selected)
                            st.info(df["SP_JOB_SCRIPT"][0])             
                    else:
                        runid_sel='\''+ '\',\''.join(map(str, runid_sel)) +'\''
                    
                        STORED_PROC_RUN_ID_ARR=sql.STORED_PROC_RUN_ID_ARR.format(arg2=script_selected,arg3=runid_sel,arg4=batch_id)
                        with st.spinner("Executing script in Snowflake"):
                            df=fn.get_query_3(STORED_PROC_RUN_ID_ARR,script_selected,runid_sel)
                            #st.write(df)
                            st.write("Executed "+script_selected)
                            st.info(df["SP_JOB_SCRIPT"][0])
                if execute_btn_prl:
                    BATCH_ID_SEQ=sql.BATCH_ID_SEQ
                    df_batch_id=fn.get_model_run_date(BATCH_ID_SEQ)
                    batch_id=df_batch_id.iloc[0][0]
                    for i in runid_sel:
                        STORED_PROC_RUN_ID=sql.STORED_PROC_RUN_ID.format(arg2=script_selected,arg3=i,arg4=batch_id)
                        fn.proc_call(STORED_PROC_RUN_ID)
                        #st.write(df)
                    # st.write("Executed "+script_selected+" with run id "+str(i))
                    st.info("Executed "+script_selected+" with selected Sequence ids "+" in parallel. Please check the audit table for logs")
            with tab2:
                
                c1,c2,c3=st.columns([2,2,2])

                STAGE_NAME=sql.STAGE_NAME
                df_stage_name=fn.get_model_run_date(STAGE_NAME)

                sel_db=c1.selectbox("Select Database",df_stage_name["database_name"].unique(),key='s6')

                df_database=df_stage_name[df_stage_name["database_name"]==sel_db]
                sel_schema=c2.selectbox("Select Schema",df_database["schema_name"].unique(),key='s7')
                   
                df_schema=df_database[df_database["schema_name"]==sel_schema]
                selc_stage=c3.selectbox("Select Stage",df_schema["name"],key='s5')
                db_schema_stage=sel_db+"."+sel_schema+"."+selc_stage

                STAGE_FILES=sql.STAGE_FILES
                df_stage_files=fn.get_query_2(STAGE_FILES,db_schema_stage)
                df_stage_files.columns = df_stage_files.columns.str.upper()
                stg_inf=c2.empty()
                stg_inf.info("Select checkbox to download")

                gb = GridOptionsBuilder.from_dataframe(df_stage_files)
                gb.configure_pagination(enabled=True)
                gb.configure_selection(selection_mode="single", use_checkbox=True,pre_selected_rows=[0])
                gridoptions = gb.build()
                st.write("")
                response=AgGrid(df_stage_files,gridOptions=gridoptions,
                                update_mode=GridUpdateMode.SELECTION_CHANGED,
                                fit_columns_on_grid_load=True,
                                theme='alpine')

                sel_rows = response['selected_rows']
                if sel_rows:
                    stg_inf.write("")
                    download=st.button(label="Download Script")
                    if download:
                        try:
                            df = pd.DataFrame(sel_rows)
                            stage_file=sel_db+"."+sel_schema+"."+df["NAME"][0]
                            GET_STAGE_FILE=sql.GET_STAGE_FILE
                            dl_stage_files=fn.get_query_2(GET_STAGE_FILE,stage_file)

                            ip=dl_stage_files["file"].iloc[0]

                            op = open(dl_stage_files["file"].iloc[0].split('.gz')[0],"w") 

                            with gzip.open(ip,"rb") as ip_byte:
                                op.write(ip_byte.read().decode("utf-8"))
                                op.close()
                            
                            os.remove(dl_stage_files["file"].iloc[0])
                            st.success("Downloaded successfully in "+os.getcwd())  
                        except Exception as e:
                            st.error(e)   


            with tab3:
                c1,c2,c3=st.columns([2,3,2])
                aud_script_sel = c2.selectbox('Select Script Name',script_name['SCRIPT_NAME'].unique(),key='s4')
                aud_script_sel='\''+ aud_script_sel +'\''
                AUDIT_LOGS=sql.AUDIT_LOGS
                df_audit_logs=fn.get_query_2(AUDIT_LOGS,aud_script_sel)
                log_inf=c2.empty()
                log_inf.info("Select checkbox to download")
                gb = GridOptionsBuilder.from_dataframe(df_audit_logs)
                gb.configure_pagination(enabled=True)
                gb.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True)
                gridoptions = gb.build()
                st.write("")
                response=AgGrid(df_audit_logs,gridOptions=gridoptions,
                                update_mode=GridUpdateMode.SELECTION_CHANGED,
                                fit_columns_on_grid_load=True,
                                theme='alpine')
                sel_rows = response['selected_rows']
                if sel_rows:
                    log_inf.write("")
                    df = pd.DataFrame(sel_rows)
                    csv = df[["SEQ_ID","SCRIPT_NAME","START_TIME","END_TIME","IMPACTED_RECORD_COUNT","STATUS","ERROR_MESSAGE","BATCH_ID"]].to_csv().encode('utf-8')

                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name='Audit Logs.csv',
                        mime='text/csv',
                    )  
        else:
            st.warning("Please login to access this page") 
    else:
        st.warning("Please login to access this page")
except AttributeError:
    st.warning("Please login to access this page")