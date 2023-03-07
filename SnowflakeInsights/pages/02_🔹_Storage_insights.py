import streamlit as st

st.set_page_config(
    page_title="Snowatch App - Storage", page_icon="🔹", layout="wide"
)

from utils import charts, gui, processing
#from utils import snowflake_connector as sf
from utils import sql
import functions as fn
import plotly.express as px
st.markdown("<h1 style='text-align: center; color: black;padding: 1% 1% 1% 1%;background-color: #a2d5f2;'>Storage Insights</h1>", unsafe_allow_html=True)

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
style_table="""
thead{
background-color:#336699;
font-size: 19px;
font-weight:bold
}
tbody{
font-size: 19px;
font-weight:bold;
background-color:AliceBlue
}
.css-81oif8{
font-size: 19px;
font-weight:bold
}
.css-a51556{
    color:white
}
"""
st.markdown(f"<style>{style_table}</style>",unsafe_allow_html=True)


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
                with st.sidebar:
                    date_from, date_to = gui.date_selector()

                # Header
                # gui.icon("🔹")
                # st.title("Storage insights")

                c1,c2=st.columns(2)
                c1.markdown("<h3 style='text-align: left; color: black;'>Year To Date</h3>", unsafe_allow_html=True)
                c2.markdown("<h3 style='text-align: left; color: black;'>Month To Date</h3>", unsafe_allow_html=True)
                def top_metrics():
                    ytd_st,ytd_stg,ytd_fs,mtd_st,mtd_stg,mtd_fs=st.columns(6)
                    with ytd_st:
                        st.metric("Avg. Storage (MB)",round(df_ytd_storage.iloc[0][0],2))
                    with ytd_stg:
                        st.metric("Avg. Stage (MB)",round(df_ytd_storage.iloc[0][1],2))
                    with ytd_fs:
                        st.metric("Avg. Failsafe (MB)",round(df_ytd_storage.iloc[0][2],2))
                    with mtd_st:
                        st.metric("Avg. Storage (MB)",round(df_mtd_storage.iloc[0][0],2))
                    with mtd_stg:
                        st.metric("Avg. Stage (MB)",round(df_mtd_storage.iloc[0][1],2))
                    with mtd_fs:
                        st.metric("Avg. Failsafe (MB)",round(df_mtd_storage.iloc[0][2],2))
                    

                df_ytd_storage = fn.sql_to_dataframe(sql.YTD_AVG_STORAGE)
                df_mtd_storage = fn.sql_to_dataframe(sql.MTD_AVG_STORAGE)
                top_metrics()

                # Get data
                query = sql.STORAGE_QUERY
                df = fn.sql_to_dataframe(
                    query.format(date_from=date_from, date_to=date_to)
                )

                # Get consumption
                consumption = df["DATABASE_KILOBYTES"].sum()

                if df.empty:
                    st.caption("No data found.")
                    st.stop()
                if consumption == 0:
                    st.caption("No consumption!")
                    st.stop()

                # Resample by day
                df_resampled = processing.resample_by_day(
                    df,
                    date_column="USAGE_DATE",
                )

                # Average bytes used per day
                # credits_used_html = "Average "
                # credits_used_html += gui.underline(
                #     text=gui.pretty_print_bytes(int(df_resampled.DATABASE_BYTES.mean())),
                #     color=gui.BLUE_COLOR,
                # )
                # credits_used_html += " were used per day"

                # gui.space(1)
                # st.write(credits_used_html, unsafe_allow_html=True)

                gui.space(1)
                st.markdown("<h4 style='text-align: center; color: black;'>Storage Spend Over Time</h4>", unsafe_allow_html=True)
                # gui.subsubheader(
                #     "**Storage** spend over time",
                #     "Aggregated by day",
                # )

                # Bar chart
                chart = charts.get_bar_chart(
                    df=df_resampled,
                    date_column="USAGE_DATE",
                    value_column="DATABASE_KILOBYTES",
                )

                st.altair_chart(chart, use_container_width=True)

                st.markdown("<h4 style='text-align: center; color: black;'>Storage Usage </h4>", unsafe_allow_html=True)
                df_storage_over_time=fn.sql_to_dataframe(sql.STORAGE_OVER_TIME.format(
                                        date_from=date_from,
                                        date_to=date_to))
                fig = px.bar(df_storage_over_time, x="USAGE_DATE", y=["STORAGE","STAGE","FAILSAFE"],barmode = 'stack')
                fig.update_layout(xaxis_title='USAGE DATE',yaxis_title='STORAGE (MB)',width=1400,height=500)
                st.write(fig)
                # st.write(
                #     df_resampled.groupby(
                #         ["OBJECT_NAME", "USAGE_DATE"]
                #     ).DATABASE_BYTES.mean()
                # )

                # Group by
                df_grouped = (
                    df.groupby(["OBJECT_NAME", "USAGE_DATE"])
                    .DATABASE_BYTES.mean()
                    .reset_index()
                    .groupby("OBJECT_NAME")
                    .mean()
                    .reset_index()
                )
                # agg_config = {"DATABASE_BYTES": "sum"}
                # df_grouped = df.groupby("OBJECT_NAME").agg(agg_config).reset_index()

                # Sort and pretty print credits
                df_grouped_top_10 = df_grouped.sort_values(
                    by="DATABASE_BYTES", ascending=False
                ).head(10)

                df_grouped_top_10["AVG_DAILY_STORAGE_SIZE"] = df_grouped_top_10[
                    "DATABASE_BYTES"
                ].apply(gui.pretty_print_bytes)

                # Pretty print BYTES
                # value_pretty_print_column = "DATABASE_BYTES_PP"
                # df_grouped[value_pretty_print_column] = df_grouped["DATABASE_BYTES"].apply(
                # gui.pretty_print_bytes
                # )
                # df_grouped["AVG_DAILY_STORAGE_SIZE"] = df_grouped[
                #     "DATABASE_BYTES_PP"
                # ].apply(lambda x: x + " " * 10)

                # df_grouped = df_grouped.sort_values(
                #     by="DATABASE_BYTES",
                #     ascending=False,
                # )
                st.markdown("<h4 style='text-align: center; color: black;'>Top 10 Databases With High Storage Spend Per Day</h4>", unsafe_allow_html=True)
                # gui.subsubheader(
                #     "**Storage** spend per day",
                #     "Average",
                #     "Grouped by OBJECT_NAME",
                #     "Top 10",
                # )

                st.table(
                    gui.dataframe_with_podium(
                        df_grouped_top_10[["OBJECT_NAME", "AVG_DAILY_STORAGE_SIZE"]],
                    ),
                )
            else:
                st.warning("Please login to access this page") 
        else:
            st.warning("Please login to access this page")
    except AttributeError:
        st.warning("Please login to access this page")


if __name__ == "__main__":
    main()
