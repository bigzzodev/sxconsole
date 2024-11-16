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
        col1.metric("SOCIAL 관련기사", _fnumber(11213) + " 개", "")
        col2.metric("ILLEGAL 관련기사", _fnumber(15658) + " 개", "")
        col3.metric("CONTRACT 관련기사", _fnumber(9374) + " 개", "")
        col4.metric("ENT 관련기사", _fnumber(16917) + " 개", "")
        col5.metric("SAJAEGI 관련기사", _fnumber(8903) + " 개", "")
        col6, col7, col8, col9, col10 = st.columns(5)
        col6.metric("MUSIC 관련기사", _fnumber(10903) + " 개", "")
        col7.metric("AD 관련기사", _fnumber(4016) + " 개", "")
        col8.metric("RIP 관련기사", _fnumber(51282) + " 개", "")
        col9.metric("AWARD 관련기사", _fnumber(820) + " 개", "")
        col10.metric("NO 관련기사", _fnumber(20193) + " 개", "")

        st.divider()
        # st.markdown("*Streamlit* is **really** ***cool***.")
        # st.markdown('''
        #     :red[Streamlit] :orange[can] :green[write] :blue[text] :violet[in]
        #     :gray[pretty] :rainbow[colors] and :blue-background[highlight] text.''')
        # st.markdown("Here's a bouquet &mdash;\
        #             :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")

        multi = '''timeline

        가수 뉴스 #1
        '''
        st.markdown(multi)



        multi = '''timeline

        가수 뉴스 #2
        '''
        st.markdown(multi)



        multi = '''timeline

        가수 뉴스 #3
        '''
        st.markdown(multi)





    with tab2:
        st.markdown(f"<h4><span style='font-size:20px; color:gray;'>시스템 사용 설명</span></h4>", unsafe_allow_html=True)
        st.write('사용법 제목')
        st.caption('사용법 나열 #1')
        st.caption('사용법 나열 #2')
        st.write('')
        # st.write('국내 언론에서 "진민호" 의 기사를 파악하여, 인사이트 도출과 전략수립, 리스크관리 그리고 경쟁사 비교등에 사용할수 있도록 데모를 만들어 보았습니다.')
        # st.write('2020.01.01 부터 2024.11.04 까지의 "진민호"에 대한 국내 언론뉴스를 ""빠짐없이 모두"" 수집하여,')
        # st.write('llm (AI) 을 통한 카테코리 분류, 요약, 키워드 추출, 통계, 분석을 수행하는 시스템 입니다.')
        # st.caption('국내 언론에서 가수/그룹 의 기사를 파악하여, 인사이트 도출과 전략수립, 리스크 관리 그리고 경쟁사 비교등에 사용할수 있도록 데모를 만들어 보았습니다.')
        # st.caption('2020.01.01 부터 2024.11.04 까지의 "진민호"에 대한 국내 언론뉴스를 ""빠짐없이 모두"" 수집하여, llm (AI) 을 통한 카테코리 분류, 요약, 키워드 추출, 통계, 분석을 수행하는 시스템 입니다.')
    with tab3:
        st.markdown(f"<h4><span style='font-size:20px; color:gray;'>분류기준</span></h4>", unsafe_allow_html=True)
        st.write('- **SOCIAL** : 가수나 그룹의 법적 논란 혹은 의혹이 있는 일. 무혐의 처분을 받았더라도, 의혹이 있다면 해당됨.')
        st.write('- **ILLEGAL** : 가수나 그룹의 마약, 음주운전, sexual 이슈, 사기 가해, 도박등 법적인 잘못에 해당하는 일.')
        st.write('- **CONTRACT** : 가수나 그룹의 군대 입대 관련 내용, 가수나 그룹의 재계약 및 소속사 관련한 일.')
        st.write('- **ENT** : 가수나 그룹이 방송 활동 및 방송 출연 내용, 가수가 홍보 목적으로 방송에 출연한 내용.')
        st.write('- **SAJAEGI** : 가수나 그룹이 부당한 방법으로 홍보를 위해 사재기 한 내용.')
        st.write('- **MUSIC** : 가수나 그룹이 앨범,공연(콘서트) 등의 음악 활동.')
        st.write('- **AD** : 가수나 그룹이 광고, 엠베서더 활동을 한 내용. 가수나 그룹이 CF, 광고 혹은 캠페인 활동.')
        st.write('- **RIP** : 가수 혹은 그룹의 멤버가 사망한 일.')
        st.write('- **AWARD** : 가수나 그룹이 연말 시상식 혹은 문체부에서 수상한 일.')
        st.write('- **NO** : 위 어느 분류에도 해당하지 않은것들')
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
