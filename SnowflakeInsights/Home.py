import streamlit as st
st.set_page_config(page_title="Snowatch App", page_icon="🌀", layout="wide")
from typing import Any, Dict
from snowflake.connector import connect
from snowflake.connector.connection import SnowflakeConnection
import functions as fn
from PIL import Image

from utils import gui

#gui.icon("🌀")
st.markdown("<h1 style='text-align: center;color: #098BCB;'>Welcome to Snowatch</h1>", unsafe_allow_html=True)
style="""
.css-184tjsw p{
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

# Make sure session state is preserved
try:
    c1,c2,c3,c4=st.columns([5,3,2,1])
    image = Image.open('Snowatch_logo.png')
    c2.image(image, caption='')
    col1,col2,col3=st.columns([1,1.5,1])
    with col2:
        head=st.empty()
        head.markdown("<h4 style='text-align: center;'>Sign in to Snowflake</h4>", unsafe_allow_html=True)

        for key in st.session_state:
            st.session_state[key] = st.session_state[key]

        #st.title("Welcome to the Usage Insights app!")
        #st.sidebar.warning('Do not leave any fields empty!', icon="⚠️")
        acc_plc=st.empty()
        if 'account' not in st.session_state:
            st.session_state.account = ""
            acc = acc_plc.text_input("Account Name",key="text3")
        else: 
            acc = acc_plc.text_input("Account Name",st.session_state.account,key="text3")

        if len(acc)<=0:
            a_err=st.empty()
            #a_err.error("Account Name field cannot be Empty!")

        un_plc=st.empty()
        if 'usrname' not in st.session_state:
            st.session_state.usrname = ""
            username = un_plc.text_input("User Name",key="text1")
        else:    
            username = un_plc.text_input("User Name",st.session_state.usrname,key="text1")


        if len(username)<=0:
            u_err=st.empty()
            #u_err.error("Username field cannot be Empty!")
        sso_chkbx=st.empty()
        if 'sso' not in st.session_state:
            st.session_state.sso=sso_chkbx.checkbox("Sign in using OKTA SSO")
        else:
            st.session_state.sso=sso_chkbx.checkbox("Sign in using OKTA SSO")

        pwd_plc=st.empty()
        if not st.session_state.sso:
            if 'password_ip' not in st.session_state:
                st.session_state.password_ip = ""
                pwd = pwd_plc.text_input("Password",type='password',key="text2")
            else: 
                pwd = pwd_plc.text_input("Password",st.session_state.password_ip,type='password',key="text2")

            if len(pwd)<=0:
                p_err=st.empty()
                #p_err.error("Password field cannot be Empty!")

            st.session_state.password_ip=pwd
        st.session_state.usrname=username
        st.session_state.account=acc

        def clear_text():
            st.session_state["text1"] = ""
            st.session_state["text2"] = ""
            st.session_state["text3"] = ""
            # st.session_state["text4"] = ""
            # st.session_state["text5"] = ""
            st.session_state.clear()

    c1, c2, c3, c4 = st.columns([4,1,1,4])
    with c2:
        login_plc=st.empty()
        Login=login_plc.button('Login')
    with c3:
        reset_plc=st.empty()
        Reset=reset_plc.button('Reset',on_click=clear_text)

    if 'success_param' not in st.session_state:
        st.session_state.success_param = False

    if st.session_state.success_param:
        un_plc.info("Logged in as "+username+" Please Logout to switch User")
        head.write("")
        sso_chkbx.write("")
        pwd_plc.write("")
        acc_plc.write("")
        login_plc.write("")
        reset_plc.write("")
        logout=st.sidebar.button("Logout")
        if logout:
            un_plc.write("")
            st.success("Successfully Logged out "+username)
            st.button('Login Again',on_click=clear_text)
            # Login_agn=st.button('Login Again')
            # if Login_agn:
            #     st.session_state.clear_text()
    else:
        if Login:
            #if len(username)>0 and len(pwd)>0 and len(acc)>0:        
                try: 
                    if st.session_state.sso:
                        input={'user':st.session_state.usrname,'account':st.session_state.account}
                        browser=True
                    else:
                        input={'user':st.session_state.usrname,'password':st.session_state.password_ip,'account':st.session_state.account}
                        browser=False       
                    snowflake_connector = fn.get_connector(      
                    secrets_key="sf_usage_app",  
                    input_params=input,#'warehouse':st.session_state.whname,'role':st.session_state.role
                    use_browser=browser,)
                    un_plc.success("Logged In as {}. Please choose a page".format(st.session_state.usrname))
            
                    st.session_state.success_param = True 
                    head.write("")
                    sso_chkbx.write("")
                    pwd_plc.write("")
                    acc_plc.write("")
                    login_plc.write("")
                    reset_plc.write("")
                    logout=st.sidebar.button("Logout")
    
                except:        
                    st.error("Incorrect Username/Password")
            # else:
            #     col2.error("Please enter all the fields")

    if Reset:
        st.session_state.password_ip=""
        st.session_state.usrname=""
        st.session_state.account=""
    

    st.sidebar.info("Choose a page!")
    # st.markdown(
    #     """
    # This app provides insights on a demo Snowflake account usage.

    # ### Get started!

    # 👈 Select a page in the sidebar!
    #     """
    # )
except Exception as e:
    st.error(e) 