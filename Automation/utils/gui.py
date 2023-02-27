import streamlit as st



BLUE_COLOR = "#1c83e1"


def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )



if __name__ == "__main__":
    pass
