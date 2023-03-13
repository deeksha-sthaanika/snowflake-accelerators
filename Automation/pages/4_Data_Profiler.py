import streamlit as st # web development
st.set_page_config(page_title="Data Profiler", page_icon="gear.png", layout="wide")
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
from utils import sql as sql
import functions as fn
import ydata_profiling as pp
from ydata_profiling import compare
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

            TABLE=sql.TABLE
            df_table=fn.get_query_data(TABLE,st.session_state.usrname)

            df_table=df_table[df_table["owner"]!='']

            c1,c2,c3,c4=st.columns(4)

            db=c1.selectbox("Select Database",df_table["database_name"].unique(),key='s3')

            sch=c2.selectbox("Select Schema",df_table[df_table["database_name"]==db].schema_name.unique(),key='s4')

            table_sel=c3.selectbox("Select Table",df_table[(df_table["database_name"]==db) & (df_table["schema_name"]==sch)].name,key='s5')

            sample_sel=c4.number_input("Enter Sample percentage",min_value=10.0,max_value=100.0)

            table_name=db+"."+sch+"."+table_sel

            COLUMNS=sql.COLUMNS.format(arg2=db,arg3=sch,arg4=table_sel)
            df_cols=fn.get_query_data(COLUMNS,st.session_state.usrname)

            cl1,cl2=st.columns(2)
            cl1.markdown("<p style='margin-bottom: 15px;'><b>Select Columns to profile:</b></p>", unsafe_allow_html=True) 
            check_box=cl1.empty()
            multi_select=cl1.empty()
            select_all = check_box.checkbox("Select all",value=True)

            
            if select_all:
                cols_sel = multi_select.multiselect('Select Columns to profile:', ['All selected'], ['All selected'], disabled=True, label_visibility='collapsed',key='m1')
                cols_sel = list(df_cols["COLUMN_NAME"])
            else:
                cols_sel = cl1.multiselect('Select Columns to profile:',df_cols,df_cols["COLUMN_NAME"].head(2), label_visibility='collapsed',key='m2')
                
            cols_sel_str='\''+ ','.join(map(str, cols_sel)) +'\''
            # st.write('"'+ '","'.join(map(str, cols_sel)) +'"')

            # st.write(cols_sel)
            cl2.markdown("<p style='margin-bottom: 15px;'><b>Select Columns for interaction:</b></p>", unsafe_allow_html=True) 
            check_box2=cl2.empty()
            multi_select2=cl2.empty()
            select_all2 = check_box2.checkbox("Select all",value=True,key='chck1')

            
            if select_all2:
                cols_sel_interaction = multi_select2.multiselect('Select Columns for interaction:', ['All selected'], ['All selected'], disabled=True, label_visibility='collapsed',key='m3')
                cols_sel_interaction=cols_sel
            else:
                cols_sel_interaction = cl2.multiselect('Select Columns to profile:',cols_sel,cols_sel[0], label_visibility='collapsed',key='m4')
            
            # cols_sel_interaction=cl2.multiselect("select columns for interaction",cols_sel,cols_sel[0])
            # cols_sel_interaction='\''+ ','.join(map(str, cols_sel_interaction)) +'\''
            st.write("")
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

            def profiling_data_with_pandas(): 
                PROFILE=sql.PROFILE_SINGLE.format(arg2=table_name,arg3=sample_sel,arg4=cols_sel_str,arg5=cols_sel_interaction,arg6=sensitive,arg7=minimal)

                df_profile =fn.runquery(PROFILE,st.session_state.usrname)
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
except Exception as e:
    if str(e).__contains__('success_param'):
        st.error("Please login to access this page")
    else:
        st.error(e)



