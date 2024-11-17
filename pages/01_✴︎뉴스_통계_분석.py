import streamlit as st
import numpy as np
import pandas as pd
import json
# from streamlit_echarts import st_echarts
from analytics import ST_ANALYTICS

# ------------------------------------------------------------------------------------------------------------------------
def main():
    # st.title("뉴스기사 분석")
    # st.header("뉴스기사 분석")
    # st.subheader("뉴스기사 분석")
    # st.write('뉴스기사 **분석** 내용')
    def _store_value():
        st.session_state["xselected"] = st.session_state["_xselected"]

    # 임시 키에 값 로드 함수
    def _load_value():
        if "xselected" in st.session_state:
            st.session_state["_xselected"] = st.session_state["xselected"]

    with st.sidebar:
        st.subheader("뉴스기사 :blue[통계 분석]")
        singer_opt = list(ST_ANALYTICS.keys())
        _load_value()
        selected = st.selectbox(
            label="분석할 가수를 선택하세요",
            options=singer_opt,
            key="_xselected",
            on_change=_store_value
        )
        func, year_opt = ST_ANALYTICS[selected]

    # func(selected_singer, selected_year)
    func(selected)

# ------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # page_icon=":chart_with_upwards_trend:
    st.set_page_config(page_icon = ':sparkles:', page_title = 'Musicow TechLab', layout = 'wide',)

    hide_streamlit_style = """
        <style>
        [data-testid="stToolbar"] {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        </style>
        """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    main()


