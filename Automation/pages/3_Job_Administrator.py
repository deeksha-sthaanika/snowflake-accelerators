import streamlit as st # web development
st.set_page_config(page_title="Job Automation", page_icon="gear.png", layout="wide")
import pandas as pd # read csv, df manipulation
from utils import sql as sql
import os
import time
import functions as fn
from random import randint
from PIL import Image
from st_aggrid import AgGrid,GridUpdateMode,DataReturnMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
# from .session_state import get_session_state

with st.container():
    cola,colb=st.columns([1,4])
    with cola:
        image1 = Image.open('Fractal-Logo-WithBL.png')
        # st.image(image1,width=150)
    with colb:
        st.write("")
        # st.markdown("<h3 style='text-align: left; color: #016299;padding: 0% 0% 0% 0%;font-size:34px'> | Speed Reliability Insights</h3>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<h1 style='text-align: center; color: black;padding: 1% 1% 1% 1%;background-color: #a2d5f2;'>Job Administrator</h1>", unsafe_allow_html=True)
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
div.stButton > button:hover {
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
style="""
.css-184tjsw p{
font-weight:bold;
font-size:15px;
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
background-color:midnightblue;
font-size: 19px;
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
            def clear_form(uploaded_file):
                st.session_state["q_name"]=""
                st.session_state["q_sql"]=""
                st.session_state["q_run"]=1
                del st.session_state["file"]
                uploaded_file = file_up.file_uploader("Choose file ",key='q_file_replace')
                # uploaded_file.seek(0)
                # state.file_key=str(randint(1000, 100000000))

            def save_uploadedfile(uploadedfile):
                with open(os.path.join(uploadedfile.name),"wb") as f:
                    f.write(uploadedfile.getbuffer())

            def put_file_in_stage(file_nm, stage_nm) -> bool:
                PUT_FILE=sql.PUT_FILE.format(arg2=file_nm,arg3=stage_nm)
                df_stage=fn.get_query_data(PUT_FILE,st.session_state.usrname)

            ROLE=sql.ROLE
            df_role=fn.get_query_data(ROLE,st.session_state.usrname)
            if 'role' not in st.session_state:
                role=st.sidebar.selectbox("Select Role",df_role["role"],key='role')
            else:    
                role=st.sidebar.selectbox("Select Role",df_role["role"],index=list(df_role["role"]).index(st.session_state.role),key='role')
            
            WAREHOUSE=sql.WAREHOUSE
            df_warehouse=fn.get_query_data(WAREHOUSE,st.session_state.usrname)
            wh=st.sidebar.selectbox("Select Warehouse",df_warehouse["name"],key='s2')
            
            USE_ROLE=sql.USE_ROLE.format(arg2=role)
            df=fn.get_query_data(USE_ROLE,st.session_state.usrname)
            
            USE_WAREHOUSE=sql.USE_WAREHOUSE.format(arg2=wh)
            df=fn.get_query_data(USE_WAREHOUSE,st.session_state.usrname)

            USE_DATABASE=sql.USE_DATABASE
            df=fn.get_query_data(USE_DATABASE,st.session_state.usrname)

            USE_SCHEMA_NAME=sql.USE_SCHEMA_NAME
            df=fn.get_query_data(USE_SCHEMA_NAME,st.session_state.usrname)
            
            # df_scripts=pd.DataFrame(columns=["JOB_ID","SCRIPT_NAME","RUN_ID","SQL_COMMAND","CONTINUE_ON_ERROR","IGNORE_SCRIPT"]) 
            SCRIPT_NAME=sql.SCRIPT_NAME
            df_scripts=fn.get_query_data(SCRIPT_NAME,st.session_state.usrname)

            df_scripts["CONTINUE_ON_ERROR"]=df_scripts["CONTINUE_ON_ERROR"].astype(str)

            tab1,tab2,tab3=st.tabs(["Configure New Jobs","Configure Existing Jobs","Configure New Tasks"])
            with tab1:
                st.subheader("Create Jobs")
                entry_sel=st.radio("How do you want to load?",["Single Line","Bulk Load"],horizontal=True)

                if entry_sel=="Single Line":
                    # st.write(st.session_state)
                    # st.write("Beginning")
                    # time.sleep(10)
                    # st.write("Sleep done")
                    if 'q_jname' not in st.session_state:
                        jobname=st.text_input("Job Script Name",key='q_name')
                    else:
                        jobname=st.text_input("Job Script Name",st.session_state.q_jname,key='q_name')
                    st.session_state.q_jname=jobname
                    df_jobname_sel=df_scripts[df_scripts["SCRIPT_NAME"]==jobname]

                    with st.expander("View Sequence Ids"):
                        st.write(df_jobname_sel)

                    if 'q_rid' not in st.session_state:
                        runid=st.number_input("Sequence Id",key='q_run',min_value=1,step=1)
                    else:
                        runid=st.number_input("Sequence Id",st.session_state.q_rid,key='q_run',min_value=1,step=1)
                    
                    SEQ_ID=sql.SEQ_ID.format(arg2=jobname)
                    df_runid=fn.get_query_data(SEQ_ID,st.session_state.usrname)
                    run_lst=list(df_runid["SEQ_ID"])

                    if runid in run_lst:
                        st.error("Sequence Id Exists")
                    else:
                        job_sel=st.radio("Choose one",("File","SQL Command"),horizontal=True)
                        st.info("Please note to use semicolon(;) as delimiter to segregate multiple queries")
                        if job_sel=='File':

                            STAGE=sql.STAGE
                            df_stage=fn.get_query_data(STAGE,st.session_state.usrname)
                            stage=st.selectbox("Staging Area ",df_stage["name"])
                            # state=get_session_state()
                            # if not state.file_key:
                            #     state.file_key = str(randint(1000, 100000000))
                            file_up=st.empty()
                            if 'file' not in st.session_state:
                                uploaded_file = file_up.file_uploader("Choose file ",key='q_file_new')   
                            else:
                                uploaded_file = file_up.file_uploader("Choose file ",st.session_state.file,key='q_file')
                            st.session_state.file=uploaded_file
                        else:
                            if 'q_sql' not in st.session_state:
                                sql_input = st.text_area("SQL Command",)   
                            else:
                                sql_input = st.text_area("SQL Command",st.session_state.q_sql)
                            st.session_state.q_sql=sql_input
                        c_on_error= st.selectbox("Continue on error?",["False","True"],key='q_err')
                        
                        ignore_scrpt=st.selectbox("Ignore script?",["N","Y"],key='q_igsc')

                        cl1,cl2=st.columns([1,7])
                        execute=cl1.button('Create Job',key='q_exec')
                        reset=cl2.button('Reset Form',key='rst',on_click=clear_form,args=uploaded_file)
                        # jobid=df_runid["JOB_ID"].iloc[0]
                    
                    if (runid not in run_lst )and execute:
                        if jobname and runid and c_on_error and ignore_scrpt:
                            if job_sel=='File':
                                if uploaded_file is not None:
                                    save_uploadedfile(uploaded_file)
                                    put_file_in_stage(uploaded_file.name,stage)
                                    # if len(run_lst)==0:
                                    colname="SCRIPT_NAME,SEQ_ID,SQL_COMMAND,CONTINUE_ON_ERROR,IGNORE_SCRIPT"
                                    val="'"+jobname+"',"+str(runid)+",'@"+stage+"/"+uploaded_file.name+".gz','"+c_on_error+"','"+ignore_scrpt+"'"
                                    # else:
                                    #     jobid=df_runid["JOB_ID"].iloc[0]
                                    #     colname="JOB_ID,SCRIPT_NAME,RUN_ID,SQL_COMMAND,CONTINUE_ON_ERROR,IGNORE_SCRIPT"
                                    #     val=str(jobid)+",'"+jobname+"',"+str(runid)+",'@"+stage+"/"+uploaded_file.name+".gz','"+c_on_error+"','"+ignore_scrpt+"'"

                                    INSERT_JOB_SCRIPT=sql.INSERT_JOB_SCRIPT.format(arg2=colname,arg3=val)
                                    df_insert=fn.get_query_data(INSERT_JOB_SCRIPT,st.session_state.usrname)

                                    st.success("Succesfully Inserted")
                                else:
                                    st.warning('Please upload a file')
                                
                            else:
                                # if len(run_lst)==0:
                                colname="SCRIPT_NAME,SEQ_ID,SQL_COMMAND,CONTINUE_ON_ERROR,IGNORE_SCRIPT"
                                val="'"+jobname+"',"+str(runid)+",'"+sql_input+"','"+c_on_error+"','"+ignore_scrpt+"'"
                                # else:
                                #     jobid=df_runid["JOB_ID"].iloc[0]
                                #     colname="JOB_ID,SCRIPT_NAME,RUN_ID,SQL_COMMAND,CONTINUE_ON_ERROR,IGNORE_SCRIPT"
                                #     val=str(jobid)+",'"+jobname+"',"+str(runid)+",'"+sql_input+"','"+c_on_error+"','"+ignore_scrpt+"'"

                                INSERT_JOB_SCRIPT=sql.INSERT_JOB_SCRIPT.format(arg2=colname,arg3=val)
                                df_insert=fn.get_query_data(INSERT_JOB_SCRIPT,st.session_state.usrname)

                                st.success("Succesfully Inserted")
                                st.experimental_rerun()
                        else:
                            st.warning('Please enter all the fields')
                else:
                    st.write("")
                    df_template=pd.read_csv("ConfigureJobTemplate.csv",index_col=None)
                    csv=df_template.to_csv(index=False)
                    st.download_button(label="Click here to download template",data=csv,file_name='ConfigureJobTemplate.csv',mime='text/csv',)

                    bulk_file = st.file_uploader("Choose a .csv file",type={"csv"})
                    if bulk_file is not None:
                        df=pd.read_csv(bulk_file)
                        st.write(df)
                        load_file=st.button("Load File")
                        if load_file:
                            try:
                                fn.dataframe_sql_to(df,'SNDBX_DEMO_DB','DEMO_WORK_INTERIM','JOB_SCRIPTS',st.session_state.usrname)
                                st.write("File Uploaded")
                            except:
                                st.write("Please upload file")
                    else:
                        st.error("Please upload file")
            with tab2:

                st.subheader("Update Jobs")
                script_selected = st.selectbox('Select Script Name',df_scripts['SCRIPT_NAME'].unique(),key='s3')

                df_job_script=df_scripts[df_scripts["SCRIPT_NAME"]==script_selected]

                action_sel=st.radio("Choose an action",["Edit","Delete"],horizontal=True)

                gd = GridOptionsBuilder.from_dataframe(df_job_script)
                gd.configure_pagination(enabled=True)

                if action_sel=='Edit':
                    gd.configure_selection(selection_mode="single", use_checkbox=True,pre_selected_rows=[0])
                    gridoptions = gd.build()

                    response=AgGrid(df_job_script,gridOptions=gridoptions,
                                    update_mode=GridUpdateMode.MODEL_CHANGED,
                                    fit_columns_on_grid_load=True,
                                    theme='alpine')
            
                    sel_rows = response['selected_rows']
                    df_sel_rows = pd.DataFrame(sel_rows)
                    if len(df_sel_rows)==0:
                        st.warning("Please select a row to edit")
                    else:   
                        update_filter="SCRIPT_NAME='"+df_sel_rows["SCRIPT_NAME"].iloc[0]+"' AND SEQ_ID="+str(df_sel_rows["SEQ_ID"].iloc[0])

                        if 'q_rid1' not in st.session_state:
                            runid=st.number_input("Sequence Id",key='q_run1',min_value=1,step=1)
                        else:
                            runid=st.number_input("Sequence Id",st.session_state.q_rid,key='q_run1',min_value=1,step=1)

                        run_lst=list(df_job_script["SEQ_ID"])

                        # if runid in run_lst:
                        #     st.error("Run Id Exists")
                        # else:
                        job_sel=st.radio("Choose one ",("File","SQL Command"),horizontal=True)
                        st.info("Please note to use semicolon(;) as delimiter to segregate multiple queries")
                        if job_sel=='File':

                            STAGE=sql.STAGE
                            df_stage=fn.get_query_data(STAGE,st.session_state.usrname)
                            stage=st.selectbox("Staging Area:",df_stage["name"])

                            if 'file1' not in st.session_state:
                                uploaded_file = st.file_uploader("Choose file:")   
                            else:
                                uploaded_file = st.file_uploader("Choose file:",st.session_state.file1)
                        else:
                            if 'q_sql1' not in st.session_state:
                                sql_input = st.text_area("SQL Command",df_sel_rows["SQL_COMMAND"].iloc[0])   
                            else:
                                sql_input = st.text_area("SQL Command",st.session_state.q_sql1)

                        c_on_error= st.selectbox("Continue on error?",["False","True"],key='q_err1')
                        
                        ignore_scrpt=st.selectbox("Ignore script?",["N","Y"],key='q_igsc1')

                        update=st.button("Update")
                        if update:
                            if runid and c_on_error and ignore_scrpt:
                                if runid not in run_lst:
                                    if job_sel=='File':
                                        if uploaded_file is not None:
                                            save_uploadedfile(uploaded_file)
                                            put_file_in_stage(uploaded_file.name,stage)

                                            # val=jobid+",'"+jobname+"',"+runid+",'@"+stage+"/"+uploaded_file.name+".gz','"+c_on_error+"','"+ignore_scrpt+"'"
                                            set_val="SEQ_ID="+str(runid)+",SQL_COMMAND='@"+stage+"/"+uploaded_file.name+".gz',"+"CONTINUE_ON_ERROR='"+c_on_error+"',IGNORE_SCRIPT='"+ignore_scrpt+"'"
                                            
                                            UPDATE_JOB_SCRIPT=sql.UPDATE_JOB_SCRIPT.format(arg2=set_val,arg3=update_filter)
                                            df_insert=fn.get_query_data(UPDATE_JOB_SCRIPT,st.session_state.usrname) 
                                            st.success("Updated Successfully")
                                        else:
                                            st.warning('Please upload a file')
                                    
                                    else:
                                        # val=jobid+",'"+jobname+"',"+runid+",'"+sql_input+"','"+c_on_error+"','"+ignore_scrpt+"'"
                                        set_val="SEQ_ID="+str(runid)+",SQL_COMMAND='"+sql_input+"',CONTINUE_ON_ERROR='"+c_on_error+"',IGNORE_SCRIPT='"+ignore_scrpt+"'"
                                        
                                        UPDATE_JOB_SCRIPT=sql.UPDATE_JOB_SCRIPT.format(arg2=set_val,arg3=update_filter)
                                        df_insert=fn.get_query_data(UPDATE_JOB_SCRIPT,st.session_state.usrname) 
                                        st.success("Updated Successfully")
                                        # SCRIPT_NAME=sql.SCRIPT_NAME
                                        # df_scripts=fn.get_query_data(SCRIPT_NAME)
                                else:
                                    st.error("Sequence Id Exists")
                            else:
                                st.warning('Please enter all the fields')

                else:
                    gd.configure_column("SCRIPT_NAME", headerCheckboxSelection = True)
                    gd.configure_selection(selection_mode="multiple", use_checkbox=True,pre_selected_rows=[0])
                    gridoptions = gd.build()
                    st.write("")

                    response=AgGrid(df_job_script,gridOptions=gridoptions,
                                    update_mode=GridUpdateMode.MODEL_CHANGED,
                                    fit_columns_on_grid_load=True,
                                    theme='alpine')
            
                    sel_rows = response['selected_rows']
                    df_sel_rows = pd.DataFrame(sel_rows)
                    if len(df_sel_rows)==0:
                        st.warning("Please select rows to delete")
                    else:
                        delete=st.button("Delete selected rows")
                        if delete:
                            for i in range(len(df_sel_rows)):
                                update_filter="SCRIPT_NAME='"+df_sel_rows["SCRIPT_NAME"].iloc[i]+"' AND SEQ_ID="+str(df_sel_rows["SEQ_ID"].iloc[i]) 
                                #or st.session_state.delete_btn:
                                # st.session_state.delete_btn=True
                                DELETE_JOB_SCRIPT=sql.DELETE_JOB_SCRIPT.format(arg2=update_filter)
                                df_insert=fn.get_query_data(DELETE_JOB_SCRIPT,st.session_state.usrname) 
                            st.success("Deleted Successfully")
                            st.experimental_rerun()
            with tab3:
                # st.write("WIP") 
                st.subheader("Create Tasks")

                TASK=sql.TASK
                df_task=fn.get_query_data(TASK,st.session_state.usrname)
                df_task.columns = df_task.columns.str.upper()

                # st.write(df_task)
                if 'task_name' not in st.session_state:
                    task_name=st.text_input("Task Name",key='task_name')
                else:
                    task_name=st.text_input("Task Name",st.session_state.task_name,key='task_name')
                
                if task_name not in list(df_task["NAME"]):
                    script_selected=None
                    runid_sel=None
                    sql_input_task=None

                    type_sel=st.radio("Choose Type",["Script","SQL Command"],horizontal=True)
                    if type_sel=='Script':
                        script_selected = st.selectbox('Select Script Name',df_scripts['SCRIPT_NAME'].unique(),key='ss')
                        df_script_sel=df_scripts[df_scripts["SCRIPT_NAME"]==script_selected]

                        with st.expander("View Sequence Ids"):
                            st.write(df_script_sel)

                        runid_sel=st.multiselect("Select Sequence Id",df_script_sel["SEQ_ID"],df_script_sel["SEQ_ID"].iloc[0])
                        runid_sel='\''+ '\',\''.join(map(str, runid_sel)) +'\''
                        
                        #STORED_PROC_RUN_ID_TASK=sql.STORED_PROC_RUN_ID_TASK.format(arg2=script_selected,arg3=runid_sel)
                        STORED_PROC_RUN_ID_ARR=sql.STORED_PROC_RUN_ID_TASK.format(arg2=script_selected,arg3=runid_sel)
                        
                        
                    else:
                        st.info("Please Validate the SQL before creating task!")
                        if 't_sql' not in st.session_state:
                            sql_input_task = st.text_area("SQL Command")   
                        else:
                            sql_input_task = st.text_area("SQL Command",st.session_state.t_sql)
                        STORED_PROC_RUN_ID_ARR=sql_input_task
                    
                    val=task_name+" WAREHOUSE='"+wh+"'"
                    parent=st.checkbox("Is this Root Task?")
                    if parent:
                        schedule_type=st.radio("Choose schedule type",["Cron","Minute"],horizontal=True)
                        if schedule_type=='Cron':
                            st.info("Sample cron strings :  * * * * * UTC   or   0 0 * * * America/Chicago")
                            # c1,c2=st.columns([1,5])
                            # c1.write("USING CRON ")
                            if 'cron' not in st.session_state:
                                cron=st.text_input("Cron String",key='cron')
                            else:
                                cron=st.text_input("Cron String",st.session_state.cron,key='cron')
                            sch="USING CRON "+cron
                        else:
                            # c1,c2=st.columns([5,1])
                            if 'minute' not in st.session_state:
                                minute=st.number_input("Minute",key='minute',min_value=1,max_value=11520)
                            else:
                                minute=st.number_input("Minute",st.session_state.minute,max_value=11520,key='minute')
                            # c2.write(" MINUTE")
                            sch=str(minute)+" MINUTE"
                    else:
                        child_task=st.multiselect("Choose dependent tasks",df_task["NAME"],df_task["NAME"].iloc[0])
                        child_task= ','.join(map(str, child_task))             
                    
                    create_btn=st.button("Create Task")

                    if create_btn:
                        if task_name and ((runid_sel and script_selected) or sql_input_task):
                            try:
                                if parent:               
                                    CREATE_PARENT_TASK=sql.CREATE_PARENT_TASK.format(arg2=val,arg3=sch,arg4=STORED_PROC_RUN_ID_ARR)
                                    df_create_task=fn.get_query_data(CREATE_PARENT_TASK,st.session_state.usrname)

                                    RESUME_TASK=sql.RESUME_TASK.format(arg2=task_name)
                                    df_resume_task=fn.get_query_data(RESUME_TASK,st.session_state.usrname)
                                else:
                                    CREATE_CHILD_TASK=sql.CREATE_CHILD_TASK.format(arg2=val,arg3=child_task,arg4=STORED_PROC_RUN_ID_ARR)
                                    df_create_task=fn.get_query_data(CREATE_CHILD_TASK,st.session_state.usrname)

                                    RESUME_TASK=sql.RESUME_TASK.format(arg2=task_name)
                                    df_resume_task=fn.get_query_data(RESUME_TASK,st.session_state.usrname)
                                st.success(task_name+" created successfully")
                            except Exception as e:  
                                st.error(e)
                        else:
                            st.error("Please enter all fields")


                else:
                    st.error("Task already exists")
        else:
            st.warning("Please login to access this page")               
    else:
        st.warning("Please login to access this page")
except Exception as e:
    if str(e).__contains__('success_param'):
        st.error("Please login to access this page")
    else:
        st.error(e)




