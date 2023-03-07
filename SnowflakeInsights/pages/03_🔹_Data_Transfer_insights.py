import streamlit as st

st.set_page_config(
    page_title="Snowatch App - Data Transfer",
    page_icon="🔹",
    layout="wide",
)

from utils import charts, gui, processing
#from utils import snowflake_connector as sf
from utils import sql
import functions as fn
st.markdown("<h1 style='text-align: center; color: black;padding: 1% 1% 1% 1%;background-color: #a2d5f2;'>Data Transfer Insights</h1>", unsafe_allow_html=True)

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
                # st.title("Data Transfer insights")

                # Get data
                query = sql.DATA_TRANSFER_QUERY
                df = fn.sql_to_dataframe(
                    query.format(
                        date_from=date_from,
                        date_to=date_to,
                    )
                )

                gui.space(1)
                #st.subheader("Target region")
                st.markdown("<h4 style='text-align: center; color: black;'>Data Transfer Spend Over Time</h4>", unsafe_allow_html=True)

                # Add filtering widget
                all_values = df["TARGET_REGION"].unique().tolist()
                selected_value = st.selectbox(
                    "Choose target region",
                    ["All"] + all_values,
                    0,
                )

                if selected_value == "All":
                    selected_value = all_values
                else:
                    selected_value = [selected_value]

                # Filter df accordingly
                df = df[df["TARGET_REGION"].isin(selected_value)]

                # Get consumption
                consumption = int(df["BYTES_TRANSFERRED"].sum())

                if df.empty:
                    st.caption("No data found.")
                    st.stop()
                if consumption == 0:
                    st.caption("No consumption!")
                    st.stop()

                # Sum of credits used
                credits_used_html = gui.underline(
                    text=gui.pretty_print_bytes(consumption),
                    color=gui.BLUE_COLOR,
                )
                credits_used_html += " were used"

                gui.space(1)
                st.write(credits_used_html, unsafe_allow_html=True)

                gui.space(1)
                # gui.subsubheader(
                #     "**Data Transfer** spend over time",
                #     "Aggregated by day",
                # )

                # Resample by day
                df_resampled = processing.resample_by_day(
                    df,
                    date_column="START_TIME",
                )

                # Bar chart
                chart = charts.get_bar_chart(
                    df=df_resampled,
                    date_column="START_TIME",
                    value_column="BYTES_TRANSFERRED",
                )

                st.altair_chart(chart, use_container_width=True)

                # Group by
                agg_config = {"BYTES_TRANSFERRED": "sum"}
                df_grouped = (
                    df.groupby(["TRANSFER_TYPE", "TARGET_CLOUD", "TARGET_REGION"])
                    .agg(agg_config)
                    .reset_index()
                )

                # Sort and pretty print credits
                df_grouped_top_10 = df_grouped.sort_values(
                    by="BYTES_TRANSFERRED", ascending=False
                ).head(10)

                df_grouped_top_10["BYTES_TRANSFERRED"] = df_grouped_top_10[
                    "BYTES_TRANSFERRED"
                ].apply(gui.pretty_print_bytes)

                gui.subsubheader(
                    "**Storage** spend",
                    " Grouped by TRANSFER_TYPE",
                    "Top 10",
                )

                st.table(
                    gui.dataframe_with_podium(
                        df_grouped_top_10[
                            [
                                "TRANSFER_TYPE",
                                "TARGET_CLOUD",
                                "TARGET_REGION",
                                "BYTES_TRANSFERRED",
                            ]
                        ]
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
