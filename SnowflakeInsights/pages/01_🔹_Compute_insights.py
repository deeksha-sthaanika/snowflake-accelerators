import plost
import streamlit as st

st.set_page_config(
    page_title="Usage Insights app - Compute", page_icon="🔹", layout="wide"
)

from utils import charts, gui, processing
#from utils import snowflake_connector as sf
from utils import sql as sql
import functions as fn
import altair as alt
import plotly.express as px
from datetime import date,timedelta

st.markdown("<h1 style='text-align: center; color: black;padding: 1% 1% 1% 1%;background-color: #a2d5f2;'>Compute Insights</h1>", unsafe_allow_html=True)
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

st.markdown("""
<style>
div[data-testid="metric-container"] {
   background-color: rgba(219,226,233,0.8);
   border: 1px solid rgba(28, 131, 225, 0.1);
   padding: 10% 10% 10% 10%;
   border-radius: 25px;
   color: rgb(30, 103, 119);
   width: 180px;
   height: 110px;
   overflow-wrap: break-word;
}
/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: rgba(35,86,131);
   font-size: 16px;
   font-weight:bold
}
div[data-testid="metric-container"] > div[data-testid="stMetricValue"] > div {
   font-size: 19px;
   color:rgba(28, 34, 80)
}
</style>
"""
, unsafe_allow_html=True)

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
                # Date selector widget
                # with st.sidebar:
                #     date_from, date_to = gui.date_selector()

                # Header
                #gui.icon("🔹")
                #st.title("Compute insights")
                #st.write("Inside compute page ",st.session_state.password_ip)
                c1,c2=st.columns(2)
                c1.markdown("<h3 style='text-align: left; color: black;'>Year To Date</h3>", unsafe_allow_html=True)
                c2.markdown("<h3 style='text-align: left; color: black;'>Month To Date</h3>", unsafe_allow_html=True)
                def top_metrics():
                    ytd_cc,ytd_tq,ytd_exec,mtd_cc,mtd_tq,mtd_exec=st.columns(6)
                    with ytd_cc:
                        st.metric("Credit Consumption",df_ytd_credits.iloc[0][0])
                    with ytd_tq:
                        st.metric("Total Queries",df_ytd_queries.iloc[0][0])
                    with ytd_exec:
                        st.metric("Avg. Execution Time (Seconds)",round(df_ytd_exec_time.iloc[0][0],2))
                    with mtd_cc:
                        st.metric("Credit Consumption",df_mtd_credits.iloc[0][0])
                    with mtd_tq:
                        st.metric("Total Queries",df_mtd_queries.iloc[0][0])
                    with mtd_exec:
                        st.metric("Avg. Execution Time (Seconds)",round(df_mtd_exec_time.iloc[0][0],2))
                    

                df_ytd_credits = fn.sql_to_dataframe(sql.YTD_CREDIT_CONSUMPTION)
                df_ytd_queries = fn.sql_to_dataframe(sql.YTD_TOTAL_QUERIES)
                df_ytd_exec_time= fn.sql_to_dataframe(sql.YTD_AVG_EXEC_TIME)
                df_mtd_credits = fn.sql_to_dataframe(sql.MTD_CREDIT_CONSUMPTION)
                df_mtd_queries = fn.sql_to_dataframe(sql.MTD_TOTAL_QUERIES)
                df_mtd_exec_time= fn.sql_to_dataframe(sql.MTD_AVG_EXEC_TIME)

                top_metrics()

                tab1,tab2,tab3=st.tabs(["Credit Consumption","Hourly Credit Consumption","Credit Spent By Users"])
                with tab1:
                    # ----------------------
                    # ---- Service type ----
                    # ----------------------
    
                    gui.space(1)
                    date_from, date_to = gui.date_selector()
                    st.markdown("<h4 style='text-align: center; color: black;'>Compute Spend Over Days</h4>", unsafe_allow_html=True)
                    # Get data
                    query = sql.CONSUMPTION_PER_SERVICE_TYPE_QUERY
                    df = fn.sql_to_dataframe(
                        query.format(date_from=date_from, date_to=date_to)
                    )

                    # Add filtering widget per Service type
                    all_values = df["SERVICE_TYPE"].unique().tolist()
                    selected_value = st.selectbox(
                        "Choose service type",
                        ["All"] + all_values,
                        0,
                    )

                    if selected_value == "All":
                        selected_value = all_values
                    else:
                        selected_value = [selected_value]

                    # Filter df accordingly
                    df = df[df["SERVICE_TYPE"].isin(selected_value)]

                    # Get consumption
                    consumption = int(df["CREDITS_USED"].sum())

                    if df.empty:
                        st.caption("No data found.")
                    elif consumption == 0:
                        st.caption("No consumption found.")
                    else:
                        # Sum of credits used
                        # credits_used_html = gui.underline(
                        #     text=gui.pretty_print_credits(consumption),
                        # )
                        # credits_used_html += " were used"

                        # gui.space(1)
                        # st.write(credits_used_html, unsafe_allow_html=True)

                        # gui.space(1)
                        # gui.subsubheader(
                        #     "**Compute** spend over time",
                        #     "Aggregated by day",
                        # )

                        # Resample by day
                        df_resampled = processing.resample_by_day(
                            df,
                            date_column="START_TIME",
                        )

                        # Bar chart
                        bar_chart = charts.get_bar_chart(
                            df=df_resampled,
                            date_column="START_TIME",
                            value_column="CREDITS_USED",
                        )

                        st.altair_chart(bar_chart, use_container_width=True)

                        # Group by
                        agg_config = {"CREDITS_USED": "sum"}
                        df_grouped = (
                            df.groupby(["NAME", "SERVICE_TYPE"]).agg(agg_config).reset_index()
                        )
                        
                        # Sort and pretty print credits
                        df_grouped_top_10 = df_grouped.sort_values(
                            by="CREDITS_USED", ascending=False
                        ).head(10)
                        
                        st.markdown("<h4 style='text-align: center; color: black;'>Top 10 Warehouse With High Credit Consumption</h4>", unsafe_allow_html=True)
                        col1,col2,col3=st.columns([3,2,2])
                        with col2:
                            format1 = st.radio('Choose a Visual',('Graph form', 'Tabular form'),horizontal=True,key='r1')
                        if format1 == 'Graph form':
                            fig = px.bar(df_grouped_top_10, x='NAME', y='CREDITS_USED')
                            fig.update_layout(xaxis_title='WAREHOUSE NAME',yaxis_title='CREDITS USED',width=1500)
                            st.write(fig)
                        else:
                            dl1,dl2=st.columns([6,1])
                            df_grouped_top_10["CREDITS_USED"] = df_grouped_top_10[
                                "CREDITS_USED"
                            ].apply(gui.pretty_print_credits)
                            csv=df_grouped_top_10.to_csv().encode('utf-8')
                            with dl2:st.download_button(label="Download Table",data=csv,file_name='Top 10 warehouse with high consumption.csv',mime='text/csv')
                            st.table(
                                gui.dataframe_with_podium(
                                    df_grouped_top_10,
                                )[["NAME", "SERVICE_TYPE", "CREDITS_USED"]]
                            )

                    # -------------------
                    # ---- Warehouse ----
                    # -------------------

                    #st.subheader("Warehouse")
                    st.markdown("<h4 style='text-align: center; color: black;'>Warehouse Usage By Time</h4>", unsafe_allow_html=True)

                    # Get data
                    warehouse_usage_hourly = fn.sql_to_dataframe(
                        sql.WAREHOUSE_USAGE_HOURLY.format(
                            date_from=date_from,
                            date_to=date_to,
                        )
                    )

                    # Add filtering widget per Warehouse name
                    warehouses = warehouse_usage_hourly.WAREHOUSE_NAME.unique()
                    selected_warehouse = st.selectbox(
                        "Choose warehouses",
                        warehouses.tolist()
                    )

                    # Filter accordingly
                    warehouse_usage_hourly_filtered = warehouse_usage_hourly[
                        warehouse_usage_hourly.WAREHOUSE_NAME.eq(selected_warehouse)
                    ]

                    # Resample so that all the period has data (fill with 0 if needed)
                    warehouse_usage_hourly_filtered = processing.resample_date_period(
                        warehouse_usage_hourly_filtered,
                        date_from,
                        date_to,
                        value_column="CREDITS_USED_COMPUTE",
                    )

                    gui.subsubheader("Time-histogram of **warehouse usage**")

                    plost.time_hist(
                        data=warehouse_usage_hourly_filtered,
                        date="START_TIME",
                        x_unit="day",
                        y_unit="hours",
                        color={
                            "field": "CREDITS_USED_COMPUTE",
                            "scale": {
                                "scheme": charts.ALTAIR_SCHEME,
                            },
                        },
                        aggregate=None,
                        legend=None,
                    )

                    # -----------------
                    # ---- Queries ----
                    # -----------------

                    # st.subheader("Queries")

                    # Get data
                    queries_data = fn.get_queries_data(
                        date_from,
                        date_to,
                    )

                    # Top-3 longest queries
                    st.markdown("<h4 style='text-align: center; color: black;'>Top-3 Long Running Queries</h4>", unsafe_allow_html=True)
                    queries_podium_df = gui.dataframe_with_podium(
                        queries_data, "DURATION_SECS"
                    ).head(3)

                    # Only show if at least three queries!
                    if len(queries_podium_df) >= 3:
                        with st.expander("🔎 Zoom into top-3 long running queries in detail"):
                            for query in queries_podium_df.itertuples():
                                st.caption(f"{query.Index} {query.DURATION_SECS_PP}")
                                st.code(query.QUERY_TEXT_PP, "sql")

                with tab2:
                    c1,c2,c3,c4=st.columns([2,3,3,2])
                    max_date=date.today()
                    min_date=max_date-timedelta(days=30)
                    date_calendar_hour = c2.date_input('Select Date Range', value = (max_date-timedelta(days=7),max_date), min_value= min_date, max_value = max_date,key='dr1')
                    try:
                        warehouse_usage_hr = fn.sql_to_dataframe(
                            sql.WAREHOUSE_USAGE_HOURLY.format(
                                date_from=date_calendar_hour[0],
                                date_to=date_calendar_hour[1]))
                    except IndexError:
                        st.warning("⚠️ Select both minimum and maximum date")
                    sel_wh=c3.selectbox("Select Warehouse",warehouse_usage_hr["WAREHOUSE_NAME"].unique())
                    warehouse_usage_hr=warehouse_usage_hr[warehouse_usage_hr["WAREHOUSE_NAME"]==sel_wh]
                    st.markdown("<h4 style='text-align: center; color: black;'>Average Hour-By-Hour Consumption</h4>", unsafe_allow_html=True)
                    col1,col2,col3=st.columns([3,2,2])
                    with col2:
                        format1 = st.radio('Choose a Visual',('Graph form', 'Tabular form'),horizontal=True,key='r2')
                    if format1 == 'Graph form':
                        fig = px.line(warehouse_usage_hr, x="START_TIME", y="CREDITS_USED_COMPUTE",markers=True,custom_data=["WAREHOUSE_NAME"]).update_traces(hovertemplate='WAREHOUSE = %{customdata[0]}<br>TIMESTAMP = %{x}<br>CREDITS USED = %{y}<br><extra></extra>')
                        fig.update_layout(xaxis_title='TIMESTAMP',yaxis_title='CREDITS USED',width=1400,height=700)
                        st.write(fig)
                    else:
                        dl1,dl2=st.columns([6,1])
                        warehouse_usage_hr["CREDITS_USED_COMPUTE"]=warehouse_usage_hr["CREDITS_USED_COMPUTE"].map("{:.2f}".format)
                        csv=warehouse_usage_hr.to_csv().encode('utf-8')
                        with dl2:st.download_button(label="Download Table",data=csv,file_name='Average Hour-By-Hour Consumption.csv',mime='text/csv')
                        st.table(warehouse_usage_hr.head(20))

                    gui.space(1)
                    #gui.hbar()
                    st.markdown("<h4 style='text-align: center; color: black;'>Average Query Volume By Hour</h4>", unsafe_allow_html=True)
                    try:
                        avg_query_volume = fn.sql_to_dataframe(
                            sql.AVERAGE_QUERY_VOLUME.format(
                                date_from=date_calendar_hour[0],
                                date_to=date_calendar_hour[1]))
                    except IndexError:
                        st.warning("⚠️ Select both minimum and maximum date")
                    avg_query_volume=avg_query_volume[avg_query_volume["WAREHOUSE_NAME"]==sel_wh]
                    col1,col2,col3=st.columns([3,2,2])
                    with col2:
                        format1 = st.radio('Choose a Visual',('Graph form', 'Tabular form'),horizontal=True,key='r3')
                    if format1 == 'Graph form':
                        fig = px.line(avg_query_volume, x="QUERY_START_HOUR", y="NUM_QUERIES",markers=True,custom_data=["WAREHOUSE_NAME"]).update_traces(hovertemplate='WAREHOUSE = %{customdata[0]}<br>TIMESTAMP = %{x}<br>NO. OF QUERIES = %{y}<br><extra></extra>')
                        fig.update_layout(xaxis_title='TIMESTAMP',yaxis_title='NUMBER OF QUERIES',width=1400,height=700)
                        st.write(fig)
                    else:
                        dl1,dl2=st.columns([6,1])
                        avg_query_volume["NUM_QUERIES"]=avg_query_volume["NUM_QUERIES"].astype(str)
                        csv=avg_query_volume.to_csv().encode('utf-8')
                        with dl2:st.download_button(label="Download Table",data=csv,file_name='Average Query Volume By Hour.csv',mime='text/csv')
                        st.table(avg_query_volume.head(20))
                    
                    st.markdown("<h4 style='text-align: center; color: black;'>Daily Credits By Type</h4>", unsafe_allow_html=True)
                    c1,c2,c3,c4=st.columns([2,2,2,2])
                    max_date=date.today()
                    min_date=max_date-timedelta(days=30)
                    date_calendar_hour = c2.date_input('Select Date Range', value = (max_date-timedelta(days=7),max_date), min_value= min_date, max_value = max_date,key='dr2')
                    try:
                        df_daily_credits_type=fn.sql_to_dataframe(sql.DAILY_CREDITS_BY_TYPE.format(
                                            date_from=date_calendar_hour[0],
                                            date_to=date_calendar_hour[1]))
                        df_daily_credits_type.fillna(0,inplace=True)
                    except IndexError:
                        st.warning("⚠️ Select both minimum and maximum date")
                    format1 = c3.radio('Choose a Visual',('Graph form', 'Tabular form'),horizontal=True,key='r5')
                    if format1 == 'Graph form':
                        fig = px.bar(df_daily_credits_type, x="USAGE_DATE", y=["WAREHOUSE_CREDITS","PIPE_CREDITS","MVIEW_CREDITS",
                                                                            "CLUSTERING_CREDITS","READER_CREDITS"],barmode = 'stack')
                        fig.update_layout(xaxis_title='USAGE DATE',yaxis_title='CREDITS',width=1400,height=700)
                        st.write(fig)
                    else:
                        dl1,dl2=st.columns([6,1])
                        csv=df_daily_credits_type.to_csv().encode('utf-8')
                        with dl2:st.download_button(label="Download Table",data=csv,file_name='Daily Credits By Type.csv',mime='text/csv')
                        st.table(df_daily_credits_type.head(20))

                with tab3:

                    # -------------
                    # --- Users ---
                    # -------------

                    #st.subheader("Users")
                    st.caption(f"Your selection is from **{date_from}** to **{date_to}**")
                    st.markdown("<h4 style='text-align: center; color: black;'>Credits Spent By Users</h4>", unsafe_allow_html=True)
                    # Get data
                    users_data = fn.sql_to_dataframe(
                        sql.USERS_QUERY.format(
                            date_from=date_from,
                            date_to=date_to,
                        )
                    )

                    col1,col2,col3=st.columns([3.5,2,2])
                    with col2:
                        format1 = st.radio('Choose a Visual',('Graph form', 'Tabular form'),horizontal=True,key='r4')
                    if format1 == 'Graph form':
                        fig = px.bar(users_data, x='APPROXIMATE_CREDITS_USED', y='USER_NAME',orientation='h')
                        fig.update_layout(xaxis_title='CREDITS USED',yaxis_title='USER NAME',width=1500)
                        st.write(fig)
                    else:
                        dl1,dl2=st.columns([6,1])
                        users_data["APPROXIMATE_CREDITS_USED"] = users_data["APPROXIMATE_CREDITS_USED"].apply(gui.pretty_print_credits)
                        csv=users_data.to_csv().encode('utf-8')
                        with dl2:st.download_button(label="Download Table",data=csv,file_name='Credits Spent By Users.csv',mime='text/csv')
                        st.table(gui.dataframe_with_podium(users_data))
                
            else:
                st.warning("Please login to access this page") 
        else:
            st.warning("Please login to access this page")
    except AttributeError:
        st.warning("Please login to access this page")


if __name__ == "__main__":
    main()
