import streamlit as st # web development
st.set_page_config(page_title="Job Automation", page_icon="gear.png", layout="wide")
import pandas as pd # read csv, df manipulation
from utils import sql as sql
import os
import functions as fn
from PIL import Image
from st_aggrid import AgGrid,GridUpdateMode,DataReturnMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

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
            def save_uploadedfile(uploadedfile):
                with open(os.path.join(uploadedfile.name),"wb") as f:
                    f.write(uploadedfile.getbuffer())

            def put_file_in_stage(file_nm, stage_nm) -> bool:
                PUT_FILE=sql.PUT_FILE
                df_stage=fn.get_query_3(PUT_FILE,file_nm,stage_nm)

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
            
            # df_scripts=pd.DataFrame(columns=["JOB_ID","SCRIPT_NAME","RUN_ID","SQL_COMMAND","CONTINUE_ON_ERROR","IGNORE_SCRIPT"]) 
            SCRIPT_NAME=sql.SCRIPT_NAME
            df_scripts=fn.get_model_run_date(SCRIPT_NAME)

            df_scripts["CONTINUE_ON_ERROR"]=df_scripts["CONTINUE_ON_ERROR"].astype(str)

            tab1,tab2,tab3=st.tabs(["Configure New Jobs","Configure Existing Jobs","Configure New Tasks"])
            with tab1:
                st.subheader("Create Jobs")
                entry_sel=st.radio("How do you want to load?",["Single Line","Bulk Load"],horizontal=True)

                if entry_sel=="Single Line":
                    if 'q_jname' not in st.session_state:
                        jobname=st.text_input("Job Script Name",key='q_name')
                    else:
                        jobname=st.text_input("Job Script Name",st.session_state.q_jname,key='q_name')

                    df_jobname_sel=df_scripts[df_scripts["SCRIPT_NAME"]==jobname]

                    with st.expander("View Sequence Ids"):
                        st.write(df_jobname_sel)

                    if 'q_rid' not in st.session_state:
                        runid=st.number_input("Sequence Id",key='q_run',min_value=1,step=1)
                    else:
                        runid=st.number_input("Sequence Id",st.session_state.q_rid,key='q_run',min_value=1,step=1)
                    
                    SEQ_ID=sql.SEQ_ID
                    df_runid=fn.get_query_2(SEQ_ID,jobname)
                    run_lst=list(df_runid["SEQ_ID"])

                    if runid in run_lst:
                        st.error("Sequence Id Exists")
                    else:
                        job_sel=st.radio("Choose one",("File","SQL Command"),horizontal=True)

                        if job_sel=='File':

                            STAGE=sql.STAGE
                            df_stage=fn.get_model_run_date(STAGE)
                            stage=st.selectbox("Staging Area ",df_stage["name"])

                            if 'file' not in st.session_state:
                                uploaded_file = st.file_uploader("Choose file ")   
                            else:
                                uploaded_file = st.file_uploader("Choose file ",st.session_state.file)
                        else:
                            if 'q_sql' not in st.session_state:
                                sql_input = st.text_area("SQL Command",)   
                            else:
                                sql_input = st.text_area("SQL Command",st.session_state.q_sql)

                        c_on_error= st.selectbox("Continue on error?",["False","True"],key='q_err')
                        
                        ignore_scrpt=st.selectbox("Ignore script?",["N","Y"],key='q_igsc')

                        execute=st.button('Create Job',key='q_exec')
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

                                    INSERT_JOB_SCRIPT=sql.INSERT_JOB_SCRIPT
                                    df_insert=fn.get_query_3(INSERT_JOB_SCRIPT,colname,val)

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

                                INSERT_JOB_SCRIPT=sql.INSERT_JOB_SCRIPT
                                df_insert=fn.get_query_3(INSERT_JOB_SCRIPT,colname,val)

                                st.success("Succesfully Inserted")
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
                                fn.dataframe_sql_to(df,'SNDBX_DEMO_DB','DEMO_WORK_INTERIM','JOB_SCRIPTS')
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

                        if job_sel=='File':

                            STAGE=sql.STAGE
                            df_stage=fn.get_model_run_date(STAGE)
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
                                            
                                            UPDATE_JOB_SCRIPT=sql.UPDATE_JOB_SCRIPT
                                            df_insert=fn.get_query_3(UPDATE_JOB_SCRIPT,set_val,update_filter) 
                                            st.success("Updated Successfully")
                                        else:
                                            st.warning('Please upload a file')
                                    
                                    else:
                                        # val=jobid+",'"+jobname+"',"+runid+",'"+sql_input+"','"+c_on_error+"','"+ignore_scrpt+"'"
                                        set_val="SEQ_ID="+str(runid)+",SQL_COMMAND='"+sql_input+"',CONTINUE_ON_ERROR='"+c_on_error+"',IGNORE_SCRIPT='"+ignore_scrpt+"'"
                                        
                                        UPDATE_JOB_SCRIPT=sql.UPDATE_JOB_SCRIPT
                                        df_insert=fn.get_query_3(UPDATE_JOB_SCRIPT,set_val,update_filter) 
                                        st.success("Updated Successfully")
                                        # SCRIPT_NAME=sql.SCRIPT_NAME
                                        # df_scripts=fn.get_model_run_date(SCRIPT_NAME)
                                else:
                                    st.error("Sequence Id Exists")
                            else:
                                st.warning('Please enter all the fields')

                else:
                    gd.configure_column("SCRIPT_NAME", headerCheckboxSelection = True)
                    gd.configure_selection(selection_mode="multiple", use_checkbox=True,pre_selected_rows=[0,3])
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
                            update_filter="SCRIPT_NAME='"+df_sel_rows["SCRIPT_NAME"].iloc[0]+"' AND SEQ_ID="+str(df_sel_rows["SEQ_ID"].iloc[0]) 
                            #or st.session_state.delete_btn:
                            # st.session_state.delete_btn=True
                            DELETE_JOB_SCRIPT=sql.DELETE_JOB_SCRIPT
                            df_insert=fn.get_query_2(DELETE_JOB_SCRIPT,update_filter) 
                            st.success("Deleted Successfully")
            with tab3:
                # st.write("WIP") 
                st.subheader("Create Tasks")

                TASK=sql.TASK
                df_task=fn.get_model_run_date(TASK)
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
                        
                        STORED_PROC_RUN_ID_TASK=sql.STORED_PROC_RUN_ID_TASK.format(arg2=script_selected,arg3=runid_sel)
                        
                        
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
                                    CREATE_PARENT_TASK=sql.CREATE_PARENT_TASK
                                    df_create_task=fn.get_query_4(CREATE_PARENT_TASK,val,sch,STORED_PROC_RUN_ID_ARR)

                                    RESUME_TASK=sql.RESUME_TASK
                                    df_resume_task=fn.get_query_2(RESUME_TASK,task_name)
                                else:
                                    CREATE_CHILD_TASK=sql.CREATE_CHILD_TASK
                                    df_create_task=fn.get_query_4(CREATE_CHILD_TASK,val,child_task,STORED_PROC_RUN_ID_ARR)

                                    RESUME_TASK=sql.RESUME_TASK
                                    df_resume_task=fn.get_query_2(RESUME_TASK,task_name)
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
except AttributeError:
    st.warning("Please login to access this page")



