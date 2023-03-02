import streamlit as st
st.set_page_config(page_title="Task Manager", page_icon="gear.png", layout="wide")
import pandas as pd
from datetime import datetime
import tzlocal
import graphviz
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import sql as sql
import functions as fn
from PIL import Image
from st_aggrid import AgGrid,GridUpdateMode,DataReturnMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
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
    st.markdown("<h1 style='text-align: center; color: black;padding: 1% 1% 1% 1%;background-color: #a2d5f2;'>Task Manager</h1>", unsafe_allow_html=True)
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
background-color:#8F8F8F;
font-size: 20px;
font-weight:bold
}
tbody{
font-size: 19px;
font-weight:bold;
background-color:#F2F2F2
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
            # Variable declaration START
            # file_dir = os.path.dirname(os.path.dirname(__file__))
            # task_list_file = (file_dir + '/data/task.csv')
            # task_hist_file = (file_dir + '/data/task_hist.csv')
            current_tz =  "'"+ tzlocal.get_localzone_name() + "'"
            # st.write(current_tz)
            print(tzlocal.get_localzone_name())
            # print(file_dir)
            # print(task_list_file)
            # print(task_hist_file)

            def current_dt():
                now = datetime.now()
                datetime_string = now.strftime("%d-%m-%Y %H:%M:%S")
                return datetime_string

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


            
            # @st.experimental_memo(ttl=600)
            # @st.experimental_singleton
            def load_data_task_list():
                # load_dt = current_dt()
                TASK=sql.TASK
                df_task=fn.get_query_data(TASK,st.session_state.usrname)
                df_task.columns = df_task.columns.str.upper()
        
                # df_task['CREATED_ON'] = df_task['CREATED_ON'].dt.strftime('%Y-%m-%d %H:%M:%S')

                # df_task.to_csv(task_list_file, index=False)
                final_df_task_list = df_task#pd.read_csv(task_list_file)
                loadtime_list = current_dt()
                print('Task List Data is loaded from Snowflake at: ', loadtime_list)
                return final_df_task_list, loadtime_list

            # In the below query, we are usign the TASK_HISTORY() function.
            # This function returns task activity within the last 7 days
            # or the next scheduled execution within the next 8 days.
            # Ideally, if you would like to get more information,
            # you can use the base table: SNOWFLAKE.ACCOUNT_USAGE.TASK_HISTORY.


            def load_data_task_hist():
                current_dt()
                TASK_HISTORY=sql.TASK_HISTORY.format(arg2=current_tz)
                df_hist=fn.get_query_data(TASK_HISTORY,st.session_state.usrname)

                LONG_TASK=sql.LONG_TASK
                df_long_task=fn.get_query_data(LONG_TASK,st.session_state.usrname)
                #df_hist['SCHEDULED_TIME'] = df_hist['SCHEDULED_TIME'].dt.strftime('%m-%d-%y %H:%M:%S')

                # df_hist.to_csv(task_hist_file, index=False)
                final_df_task_hist = df_hist#pd.read_csv(task_hist_file)
                loadtime_hist = current_dt()
                print('Task History Data is loaded from Snowflake at: ', loadtime_hist)
                return final_df_task_hist,df_long_task,loadtime_hist


            # Loading Data from Snowflake END


            with st.spinner("Please wait while we load the Data from Snowflake..."):
                task_list, load_dt_list = load_data_task_list()
                task_hist,df_long_task, load_dt_hist = load_data_task_hist()
                PARENT_TASK=sql.PARENT_TASK
                df_task_parent=fn.get_query_data(PARENT_TASK,st.session_state.usrname)
                df_task_parent.columns = df_task_parent.columns.str.upper()
        

                # st.success('Snowflake Data Successful loaded!', icon="✅")

            tab1,tab2,tab3,tab4,tab5 = st.tabs(["TASK SUMMARY","TASK LIST","TASK HISTORY","EXECUTE TASKS","TASK HIERARCHY"])
            
                # TAB1
            with tab1:

                fig_count = make_subplots(
                    rows=2, cols=2,
                    specs=[
                        [{"type": "indicator"}, {"type": "indicator"}],
                        [{"type": "indicator"}, {"type": "indicator"}],
                    ],
                    horizontal_spacing=0, vertical_spacing=0
                )

                total_task_count = len(task_hist)
                total_task_success = len(task_hist[task_hist['STATE'] == 'SUCCEEDED'])
                total_task_error = len(task_hist[task_hist['STATE'] == 'FAILED'])
                total_task_scheduled = len(task_hist[task_hist['STATE'] == 'SCHEDULED'])

                fig_count.add_trace(
                    go.Indicator(
                        mode="number",
                        value=total_task_count,
                        title="Total Task",

                    ),
                    row=1, col=1

                )

                fig_count.add_trace(
                    go.Indicator(
                        mode="number",
                        value=total_task_success,
                        title="Successful Runs",
                        number={'font_color': 'green'},
                    ),
                    row=1, col=2
                )

                fig_count.add_trace(
                    go.Indicator(
                        mode="number",
                        value=total_task_scheduled,
                        title="Task Scheduled",
                    ),
                    row=2, col=1
                )

                fig_count.add_trace(
                    go.Indicator(
                        mode="number",
                        value=total_task_error,
                        title="Failure Runs",
                        number={'font_color': 'red'},
                    ),
                    row=2, col=2
                )

                fig_count.update_layout(template="plotly_dark", font_family="Arial",
                                        margin=dict(l=20, r=20, t=20, b=20), width=800, height=300)
                st.plotly_chart(fig_count, use_container_width=True)
                # Summary plot for counts - END

                # Showcase timeline start
                # timeline = st_timeline(task_actual_list, groups=[], options={}, height="300px")
                # st.subheader("Selected item")
                # st.write(timeline)

                # col1 = st.columns()
                #    with col1:
                st.markdown(
                    "<h2 style='text-align: center; color: black;'>Upcoming Tasks",
                    unsafe_allow_html=True)

                now = datetime.now()

                dt_string = now.strftime("%Y-%m-%d %H:%M:%S%z")
                # print (dt_string)
                # print('11-02-22 17:00:00' >= dt_string)
                st.table(task_hist.loc[task_hist["NEXT_SCHEDULED_TIME"] >= str(dt_string), ["NAME", "DATABASE_NAME", "SCHEMA_NAME",
                                                                                    "NEXT_SCHEDULED_TIME"]].head(10))
                

                st.markdown(
                    "<h2 style='text-align: center; color: black;'>Long Running Tasks",
                    unsafe_allow_html=True)
                st.table(df_long_task[["NAME", "DATABASE_NAME", "SCHEMA_NAME","DURATION_SECONDS"]].head(10))

            # TAB2
            with tab2:
                st.markdown(
                    "<h2 style='text-align: center; color: black;'>List of Tasks",
                    unsafe_allow_html=True)
                st.info(
                    "Click on any of the task to see additonal info. Note: You can filter, export, slice and dice the below data! "
                    )
                st.markdown(
                    "<h1 style='text-align: center; color: black;'>",
                    unsafe_allow_html=True)


                def aggrid_task_list_table(df: pd.DataFrame):
                    options = GridOptionsBuilder.from_dataframe(
                        df, enableRowGroup=True, enableValue=True, enablePivot=True
                    )

                    options.configure_side_bar()

                    options.configure_selection("single",pre_selected_rows=[0])
                    selection = AgGrid(
                        df,
                        enable_enterprise_modules=True,
                        gridOptions=options.build(),
                        theme="balham",
                        update_mode=GridUpdateMode.MODEL_CHANGED,
                        allow_unsafe_jscode=True,
                    )
                    return selection


                col1, col2 = st.columns([3.5, 1])
                with col1:
                    selection = aggrid_task_list_table(df=task_list)

                with col2:
                    st.write('Below are the details: ')
                    if selection:
                        st.write("You selected:")
                        st.json(selection["selected_rows"])

            # TAB3
            with tab3:
                # tab1.subheader("History of Task")
                st.markdown(
                    "<h2 style='text-align: center; color: black;'>List of Tasks",
                    unsafe_allow_html=True)
                st.info(
                    "Please click 'Run History' to find the run history of any of the task",
                    )
                st.markdown(
                    "<h1 style='text-align: center; color: black;'>",
                    unsafe_allow_html=True)

                colms = st.columns((6))

                for col, field_name in zip(colms, ['NAME', 'DATABASE_NAME', 'SCHEMA_NAME', 'STATE', 'SCHEDULED_TIME']):
                    col.markdown("<h5 style='color: #038ed3;'>"+field_name,unsafe_allow_html=True)

                for idx, task_name in enumerate(task_list['NAME']):
                    col1, col2, col3, col4, col5, col6 = st.columns((6))
                    col1.write(task_list['NAME'][idx])
                    col2.write(task_list['DATABASE_NAME'][idx])
                    col3.write(task_list['SCHEMA_NAME'][idx])
                    col4.write(task_list['STATE'][idx])
                    col5.write(task_list['SCHEDULE'][idx])

                    placeholder = col6.empty()
                    show_more = placeholder.button("Run History", key=task_name)

                    # if button pressed
                    if show_more:
                        placeholder.button("less", key=str(idx) + "_")
                        res = task_hist.loc[task_hist['NAME'] == task_name]
                        AgGrid(res)

            # TAB4
            with tab4:
                st.markdown(
                    "<h2 style='text-align: center; color: black;'>Execute Task",
                    unsafe_allow_html=True)
                st.info(
                    "Please select a task to execute. Note: Only root tasks can be executed",
                    )
                st.markdown(
                    "<h1 style='text-align: center; color: grey;'>", unsafe_allow_html=True)


                def run_task_list(data):
                    st.markdown(f"<div id='linkto_{'Search'}'></div>", unsafe_allow_html=True)
                    execute_task_select = st.selectbox(
                        'Task Name',
                        data['NAME'].unique())

                    st.error("Do you want to run this task?")



                    database_name = data[data['NAME'] == execute_task_select]['DATABASE_NAME'].unique()
                    schema_name = data[data['NAME'] == execute_task_select]['SCHEMA_NAME'].unique()

                    task_to_be_executed = database_name + "." + schema_name + "." + execute_task_select


                    if st.button("Execute Task"):
                        st.write("we are here")
                        print("EXECUTE TASK " + task_to_be_executed[0])
                        EXECUTE_TASK=sql.EXECUTE_TASK.format(arg2=task_to_be_executed[0])
                        df_exec=fn.get_query_data(EXECUTE_TASK,st.session_state.usrname)
                        # conn.execute_string("EXECUTE TASK " + task_to_be_executed[0])
                        st.write('Task Executed Successfully. Please check your Snowflake instance for more details.')

                    st.write(
                        'Below is the run history for the executed task')
                    run_task_list_res = data.loc[data['NAME'] == execute_task_select]
                    AgGrid(run_task_list_res, theme='material')


                    return task_to_be_executed

                task_to_be_execute = run_task_list(df_task_parent)#task_hist
            with tab5:
                # TASK=sql.TASK
                # df_task=fn.get_query_data(TASK)
                # df_task.columns = df_task.columns.str.upper()
                # st.write(df_task)
                # lst=list(df_task["NAME"])
                # st.write(lst)
                st.markdown(
                    "<h2 style='text-align: center; color: black;'>Task Hierarchy", unsafe_allow_html=True)
                # st.subheader("Task Hierarchy")
                df_task=task_list
                task=st.selectbox("Choose a task",df_task["NAME"])#,lst.index('PARENT_TASK')
                st.write("")
                st.write("")
                if task not in list(df_task_parent["NAME"]):
                    st.info("You selected a child task. The graph below shows only immediate parent of the selected task along with all its children if exists")
                task_sel=df_task[df_task["NAME"]==task].DATABASE_NAME+'.'+df_task[df_task["NAME"]==task].SCHEMA_NAME+'.'+task

                def rolechart():
                    
                    # sqlstr='\select * \from table(information_schema.task_dependents(task_name => \'SNDBX_DEMO_DB.DEMO_WORK_INTERIM.PARENT_TASK\', recursive => false))\'
                    # fn.sql_to_dataframe("Use warehouse Compute_wh",st.session_state.usrname)
                    DAG=sql.DAG.format(arg2=task_sel.iloc[0])
                    rdf=fn.get_query_data(DAG,st.session_state.usrname)
                    # rdf=fn.sql_to_dataframe("SELECT PARENT,substr(F.VALUE::VARCHAR,(regexp_instr(F.VALUE::VARCHAR,'\\\.',1,2)+1)) CHILD FROM (select NAME PARENT,PREDECESSORS CHILD from table(SNDBX_DEMO_DB.information_schema.task_dependents(task_name => '"+task_sel.iloc[0]+"', recursive => TRUE)) )MAIN,TABLE(FLATTEN(MAIN.CHILD))F")
                    dot=graphviz.Digraph()
                    dot.attr("node", shape="box",fillcolor="aliceblue",style="filled")
                    dot.attr("edge", color="midnightblue",fillcolor="midnightblue")
                    dot.attr( rankdir="TB")
                    dot.node(task,fillcolor="#a2d5f2",style="filled")
                    for i in range(len(rdf)):
                        dot.edge(rdf["CHILD"][i],rdf["PARENT"][i])
                    
                    
                    st.graphviz_chart(dot,use_container_width=True)
                    
                rolechart()



            # TAB definition END

            # Sidebar definition START

            # with st.sidebar:
            #     # st.image('task.png', width=150)

            #     # st.metric(label="Run Statistics", value="10 Success", delta="5 %")
            #     if st.button('Refresh Task Data?'):
            #         # load_data_task_list.clear()
            #         # load_data_task_hist.clear()
            #         task_list, load_dt_list = load_data_task_list()
            #         task_hist, load_dt_hist = load_data_task_hist()
            #         st.sidebar.info('Data is loaded from Snowflake. If you want to reload the task data again, please click here!')
            #         time.sleep(1)

            #     st.sidebar.info(load_dt_list, icon="🕒")
        else:
            st.warning("Please login to access this page")

    else:
        st.warning("Please login to access this page")
except AttributeError:
    st.warning("Please login to access this page")
