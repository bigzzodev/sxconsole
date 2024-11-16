import streamlit as st
import numpy as np
import pandas as pd
import json

def _fnumber(num):
    return "{:,}".format(num)
# ------------------------------------------------------------------------------------------------------------------------
def all_dashboard_company(_company):
    # st.subheader(f'분석할 회사 : {_company}')


    st.subheader(f'뉴스 분석 시스템')

    tab1, tab2, tab3 = st.tabs(["전체 통계 지표", "시스템에 대한 설명", "분류기준 설명"])
    with tab1:
        col_a, col_b = st.columns(2)
        col_a.metric("총 수집 가수 수 ", _fnumber(4) + " 명", "")
        col_b.metric("총 뉴스 기사 수 ( 2020.01.01 ~ 2024.11.04 ) ", _fnumber(149279) + " 개", "")




        col1, col2, col3, col4, col5,= st.columns(5)
        col1.metric("INSURANCE 관련기사", _fnumber(11213) + " 개", "")
        col2.metric("BUSINESS 관련기사", _fnumber(15658) + " 개", "")
        col3.metric("ESG 관련기사", _fnumber(9374) + " 개", "")
        col4.metric("COMPLIANCE 관련기사", _fnumber(16917) + " 개", "")
        col5.metric("ORGANIZATION 관련기사", _fnumber(8903) + " 개", "")
        col6, col7, col8, col9, col10 = st.columns(5)
        col6.metric("MARKET 관련기사", _fnumber(10903) + " 개", "")
        col7.metric("TECHINNOV 관련기사", _fnumber(4016) + " 개", "")
        col8.metric("SPORTS 관련기사", _fnumber(51282) + " 개", "")
        col9.metric("AD 관련기사", _fnumber(820) + " 개", "")
        col10.metric("NO 관련기사", _fnumber(20193) + " 개", "")
    with tab2:
        st.markdown(f"<h4><span style='font-size:20px; color:gray;'>시스템 설명</span></h4>", unsafe_allow_html=True)
        st.write('시스템 설명..주절주절.......')
        st.write('주절주절..')
        st.write('')
        # st.write('국내 언론에서 "진민호" 의 기사를 파악하여, 인사이트 도출과 전략수립, 리스크관리 그리고 경쟁사 비교등에 사용할수 있도록 데모를 만들어 보았습니다.')
        # st.write('2020.01.01 부터 2024.11.04 까지의 "진민호"에 대한 국내 언론뉴스를 ""빠짐없이 모두"" 수집하여,')
        # st.write('llm (AI) 을 통한 카테코리 분류, 요약, 키워드 추출, 통계, 분석을 수행하는 시스템 입니다.')
        st.caption('국내 언론에서 "진민호" 의 기사를 파악하여, 인사이트 도출과 전략수립, 리스크 관리 그리고 경쟁사 비교등에 사용할수 있도록 데모를 만들어 보았습니다.')
        st.caption('2020.01.01 부터 2024.11.04 까지의 "진민호"에 대한 국내 언론뉴스를 ""빠짐없이 모두"" 수집하여, llm (AI) 을 통한 카테코리 분류, 요약, 키워드 추출, 통계, 분석을 수행하는 시스템 입니다.')
    with tab3:
        st.markdown(f"<h4><span style='font-size:20px; color:gray;'>분류기준</span></h4>", unsafe_allow_html=True)
        st.write('- **INSURANCE** : 진민호의 금융 상품이나 보험 상품에 관한 내용')
        st.write('- **BUSINESS** : 진민호의 경영 활동이나 실적과 관련된 내용')
        st.write('- **ESG** : 진민호의 사회적 책임 활동이나 ESG(환경, 사회, 지배구조)와 관련된 내용')
        st.write('- **COMPLIANCE** : 진민호과 관련된 법적 문제나 규제 이슈에 대한 내용')
        st.write('- **ORGANIZATION** : 진민호의 인사 이동이나 조직 개편과 관련된 내용')
        st.write('- **MARKET** : 진민호의 보험 및 금융 시장에서의 위치나 경쟁 상황과 관련된 내용')
        st.write('- **TECHINNOV** : 진민호의 기술 혁신이나 디지털 전환과 관련된 내용')
        st.write('- **SPORTS** : 진민호 소속 스포츠 구단이나, 스포츠 육성 및 저변확대에 관련된 내용')
        st.write('- **AD** : 진민호의 광고 캠페인이나 홍보 활동과 관련된 내용')
        st.write('- **NO** : 진민호과 관련된 특정 카테고리에 포함되지 않는 내용')
    st.divider()






# ---------------------------------------------------------------------------------------
def page_header():
    st.set_page_config(page_icon = ':sparkles:', page_title = 'TechLab', layout = 'wide',)
    # st.title('_:red[Musicow] :gray[Techlab]_ :goat:')
    # if not os.getenv("OPENAI_API_KEY"):
    #     st.info('Enter an OpenAI API Key to continue')
    #     st.stop()
    # st.divider()

# # ---------------------------------------------------------------------------------------
# def display():
#     with st.sidebar:
#         st.subheader("뉴스기사 :red[질문] 시스템")
#         # 가수별
#         singer_opt = list(ST_ANALYTICS.keys())
#         selected = st.selectbox(label="질문할 가수를 선택하세요", options=singer_opt,)
#         func, year_opt = ST_ANALYTICS[selected]
#         # selected_year = st.selectbox(label="확인할 년도를 선택하세요", options=year_opt,)
#         # st.write("You selected:", selected_year)

#     with st.sidebar:
#         clear_btn = st.button('대화 초기화')
#         # option = st.selectbox('프롬프트를 선택해 주세요', ('기본모드', 'SNS 게시글', '요약'), index=0)

#     st.subheader(f'"{selected}" 에 대해 질문하기')
#     display_main(selected, clear_btn)



# ---------------------------------------------------------------------------------------
if __name__ == '__main__':
    page_header()
    all_dashboard_company('dd')
    # _langsmith(ST_TRACE)
