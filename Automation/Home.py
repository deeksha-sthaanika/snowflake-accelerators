import streamlit as st
from snowflake.connector import connect
from snowflake.connector.connection import SnowflakeConnection
from utils import sql as sql
import functions as fn  
from PIL import Image
# footer {visibility: hidden;}

st.set_page_config(page_title="Login Page", page_icon="🏠", layout="wide")
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
st.markdown("""
<style>
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
</style>""",unsafe_allow_html=True)


# st.image('Fractal-Logo-WithBL.png',width=160)
st.markdown("<h1 style='text-align: center;color: #098BCB;'>Welcome to SnowProcSQLite</h1>", unsafe_allow_html=True)
# st.title("Welcome to the Snowflake Job Automation!")

# st.image('snowflake-logo.png',width=50)
try:
    col1,col2,col3=st.columns([1,1.5,1])
    with col2:

        st.markdown("<h4 style='text-align: center;padding: 4% 4% 4% 4%'> </h4>", unsafe_allow_html=True)


        image1 = Image.open('snowflake-logo.png')
        image2='snowflake-logo.png'
        
        # st.markdown("<p align=center><img src='"+image2+"'alt='Snowflake'></p>",unsafe_allow_html=True)
        head=st.empty()
        head.markdown("<h4 style='text-align: center;'>Sign in to Snowflake</h4>", unsafe_allow_html=True)

    # st.write(st.session_state)
    # Make sure session state is preserved
        for key in st.session_state:
            st.session_state[key] = st.session_state[key]



        wrng_plc=st.empty()
        # wrng_plc.warning('Do not leave any fields empty!', icon="⚠️")

        acc_plc=st.empty()

        if 'account' not in st.session_state:
            st.session_state.account = ""
            acc = acc_plc.text_input("Account Name",key="text3")
        else: 
            acc = acc_plc.text_input("Account Name",st.session_state.account,key="text3")

        if len(acc)<=0:
            a_err=st.empty()
            # a_err.error("Account Name field cannot be Empty!")

        un_plc=st.empty()

        if 'usrname' not in st.session_state:
            st.session_state.usrname = ""
            username = un_plc.text_input("User Name",key="text1")
        else:    
            username = un_plc.text_input("User Name",st.session_state.usrname,key="text1")


        if len(username)<=0:
            u_err=st.empty()
            # u_err.error("Username field cannot be Empty!")

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
            # p_err.error("Password field cannot be Empty!")
        # if len(username)<=0 and len(pwd)<=0 and len(acc)<=0:
        #     st.error("Please enter all the fields")
        

            st.session_state.password_ip=pwd
        st.session_state.usrname=username
        st.session_state.account=acc

        def clear_text():
            # st.write(st.session_state)
            # st.session_state["text1"] = ""
            # st.session_state["text2"] = ""
            # st.session_state["text3"] = ""
            # st.session_state.usrname=''
            # st.session_state.password_ip=''
            # st.session_state.account=''
            st.session_state.clear()
            # st.write(st.session_state)

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
        # st.write(st.session_state.usrname+"logged in. Please Logout to switch User")
        un_plc.info("Logged in as "+username+" Please Logout to switch User")
        head.write("")
        wrng_plc.write("")
        # u_err.write("")
        sso_chkbx.write("")
        pwd_plc.write("")
        # p_err.write("")
        acc_plc.write("")
        # a_err.write("")
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
            # if len(username)>0 and len(pwd)>0 and len(acc)>0 :    #and len(wh)>0 and len(role)>0    
                try: 
                    if st.session_state.sso:
                        input={'user':st.session_state.usrname,'account':st.session_state.account}
                        browser=True
                    else:
                        input={'user':st.session_state.usrname,'password':st.session_state.password_ip,'account':st.session_state.account}
                        browser=False
                    snowflake_connector = fn.get_connector(      
                    secrets_key="sf_usage_app",  
                    input_params=input,#,'warehouse':st.session_state.whname,'role':st.session_state.role
                    use_browser=browser,)
                    un_plc.success("Logged In as {}. Please choose a page".format(st.session_state.usrname))
                    
                    st.session_state.success_param = True 
                    head.write("")
                    wrng_plc.write("")
                    # un_plc.write("")
                    # u_err.write("")
                    sso_chkbx.write("")
                    pwd_plc.write("")
                    # p_err.write("")
                    acc_plc.write("")
                    # a_err.write("")
                    login_plc.write("")
                    reset_plc.write("")
                    logout=st.sidebar.button("Logout")
                    # st.write(st.session_state)
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
    # ### Get started!

    # 👈 Select a page in the sidebar!
    #     """
    # )
except Exception as e:
    st.error(e)