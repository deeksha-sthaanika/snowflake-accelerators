import plost
import streamlit as st

st.set_page_config(
    page_title="Snowflake Pricing Calculator", page_icon="🔹", layout="wide"
)


import pandas as pd
import altair as alt
import plotly.express as px
from datetime import date,timedelta
from st_aggrid import GridOptionsBuilder, AgGrid,GridUpdateMode


st.markdown("<h1 style='text-align: center; color: black;padding: 1% 1% 1% 1%;background-color: #a2d5f2;'>Snowflake Pricing Calculation</h1>", unsafe_allow_html=True)
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
</style><div class="footer"><p>Snowflake Pricing Calculator</p></div>"""
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



def generate_agrid(df):
    NameList = ["XS","Small","Medium","Large","XL","2XL","3XL","4XL"]
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("Warehouse Size", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': NameList })
    gb.configure_columns(['Warehouse Name','Maximum Clusters','Usage Per Day (hr)','No.Of Days Per Week'],editable=True)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True) 
    vgo = gb.build()
    grid_response=AgGrid(df, gridOptions=vgo, theme='alpine',fit_columns_on_grid_load=True)
    return grid_response

def add_row(grid_table):
    df = pd.DataFrame(grid_table['data'])
    new_row = [[sel_platform,sel_region,'WH', 'XS','','','','','']]
    df_empty = pd.DataFrame(new_row, columns=df.columns)
    df = pd.concat([df, df_empty], axis=0, ignore_index=True)
    df.to_csv('sample.csv', index=False)

def delete_row(df, grid):
    selected_rows = grid['selected_rows']
    if selected_rows:
        selected_indices = [i['_selectedRowNodeInfo']
                            ['nodeRowIndex'] for i in selected_rows]
        df_indices = df.index[selected_indices]
        df = df.drop(df_indices)
    return df

def get_data():
    """Reads sample.csv and return a dataframe."""
    df=pd.read_csv('sample.csv')
    return df

sel_platform=st.sidebar.selectbox("Cloud Platform",['AWS','Azure','GCP'])

if sel_platform == 'AWS':
    df_price_sheet=pd.read_excel('Snowflake_Calculator_Latest.xlsx',sheet_name = 'AWS')
elif sel_platform == 'Azure':
    df_price_sheet=pd.read_excel('Snowflake_Calculator_Latest.xlsx',sheet_name = 'Azure')
else:
    df_price_sheet=pd.read_excel('Snowflake_Calculator_Latest.xlsx',sheet_name = 'GCP')

df_aws_price=pd.read_excel('Snowflake_Calculator_Latest.xlsx',sheet_name = 'AWS')
df_azure_price=pd.read_excel('Snowflake_Calculator_Latest.xlsx',sheet_name = 'Azure')
df_gcp_price=pd.read_excel('Snowflake_Calculator_Latest.xlsx',sheet_name = 'GCP')

df_price_sheet=df_price_sheet[df_price_sheet['Platform']==sel_platform].sort_values(by=['Region'])
sel_region=st.sidebar.selectbox("Geography of application",df_price_sheet["Region"])
edition=st.sidebar.selectbox("Edition",["Business Critical","Enterprise","Standard"])
storage_type=st.sidebar.selectbox("Type of storage",["On Demand","Pre Purchase"])
#month=st.sidebar.number_input('No. of Months',min_value=1,step=1)

c1,c2=st.columns([2,2])
df_price_sheet=df_price_sheet[(df_price_sheet["Platform"]==sel_platform) & (df_price_sheet["Region"]==sel_region)]
c1.markdown("<h3 style='text-align: center; color: black;'>Storage</h3>", unsafe_allow_html=True)
with c1.form("storage_form"):
    Est_storage=st.number_input('Est. Storage Per Month(Terabyte)',min_value=1,step=1)
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    submitted = st.form_submit_button("Calculate")
if submitted:
    st.session_state.storage_cost=Est_storage*df_price_sheet[storage_type]
if "storage_cost" not in st.session_state:
    c1.metric("Storage Cost ($)",0)
else:
    c1.metric("Storage Cost ($)",st.session_state.storage_cost)

c2.markdown("<h3 style='text-align: center; color: black;'>Data Transfer</h3>", unsafe_allow_html=True)
with c2.form("data_transfer_form"):
    data_transfer=st.number_input('Data Transfer Per Month(Terabyte)',min_value=1,step=1)
    if sel_platform == 'AWS':
        Transfer_Type=st.selectbox("Transfer Type",["Same cloud provider,Same region","Same cloud provider,Different region","Different cloud provider"])
    elif sel_platform == 'Azure':
        Transfer_Type=st.selectbox("Transfer Type",["Same cloud provider,Same region","Same cloud provider,Same continent","Same cloud provider,Different continent","Different cloud provider"])
    else:
        Transfer_Type=st.selectbox("Transfer Type",["Same cloud provider,Same region","Same cloud provider,Different region,Same Continent","Same cloud provider,Different Continent","Same cloud provider,Oceania",
                                                            "Different cloud provider,Same continent","Different cloud provider,Different continent","Different cloud provider,Oceania"])
    submitted = st.form_submit_button("Calculate")
if submitted:     
    st.session_state.data_trans_cost=df_price_sheet[Transfer_Type]*data_transfer
if "data_trans_cost" not in st.session_state:
    c2.metric("Data Transfer Cost ($)",0)
else:
    c2.metric("Data Transfer Cost ($)",st.session_state.data_trans_cost)
st.markdown("<h3 style='text-align: center; color: black;'>Compute</h3>", unsafe_allow_html=True)
st.caption("Double click to add input to the columns")

if 'Reset' not in st.session_state:
    st.session_state.Reset=True
    df_raw=pd.DataFrame({'Cloud Platform':sel_platform,'Region':sel_region,'Warehouse Name':["WH"],'Warehouse Size':["XS"],'Maximum Clusters':[0],'Usage Per Day (hr)':[0],'No.Of Days Per Week':[0]})#,columns=['Cloud Platform','Region','Warehouse Name','Warehouse Size','Maximum Clusters','Usage Per Day (hr)','No.Of Days Per Week'])
    df_raw.to_csv('sample.csv', index = False)
df = get_data()
grid=st.empty()
with grid:
    grid_response=generate_agrid(df)
df = pd.DataFrame(grid_response['data'])
c1,c2,c3,c4=st.columns([4,1,1,5])
delete_row_button = c2.button("Delete Row")
if delete_row_button:
    df_del=delete_row(df, grid_response)
    try:
        with grid:
            df_del.to_csv('sample.csv', index = False)
            grid_response=generate_agrid(df_del)
    except:
        st.warning('Please select the rows to be deleted')
c3.button("Add Row", on_click=add_row, args=[grid_response])
cal=c4.button("Calculate")
df_test=df
df[["Credits Per Month","Amount Per Month ($)"]]=0
if cal:
    for i in range(len(df)):
        wh_sz=df["Warehouse Size"].iloc[i]
        if df["Cloud Platform"].iloc[i] == 'AWS':
            df_price_sheet=df_aws_price
        elif df["Cloud Platform"].iloc[i] == 'Azure':
            df_price_sheet=df_azure_price
        else:
            df_price_sheet=df_gcp_price
        df_price_sheet=df_price_sheet[(df_price_sheet["Platform"]==df["Cloud Platform"].iloc[i]) & (df_price_sheet["Region"]==df["Region"].iloc[i])]
        df["Credits Per Month"].iloc[i]=df["Maximum Clusters"].iloc[i]*df_price_sheet[wh_sz]*df["Usage Per Day (hr)"].iloc[i]*df["No.Of Days Per Week"].iloc[i]*4.345
        df["Amount Per Month ($)"].iloc[i]=df["Credits Per Month"].iloc[i]*df_price_sheet[edition]
    try:
        with grid:
            df.to_csv('sample.csv', index = False)
            grid_response=generate_agrid(df)
    except:
        st.warning("Please fill/update the required input columns")
