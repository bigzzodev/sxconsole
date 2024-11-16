import os
import json
import streamlit as st
from streamlit_echarts import st_echarts
from .chart_options import year_company_option, year_series, month_company_option, month_series, all_company_option, all_series
from annotated_text import annotated_text, annotation, parameters
from collections import defaultdict
# class_INSURANCE, class_BUSINESS, class_ESG, class_COMPLIANCE, class_ORGANIZATION, class_MARKET, class_TECHINNOV, class_SPORTS, class_AD, class_NO
SX_CLASS_NAME = ["INSURANCE", "BUSINESS", "ESG", "COMPLIANCE", "ORGANIZATION", "MARKET", "TECHINNOV", "SPORTS", "AD", "NO"]
os.environ["STREAMLIT_THEME_BASE"] = "dark"

import streamlit as st
import pandas as pd
import numpy as np
import pytz
from datetime import datetime
from datetime import date
from PIL import Image
from .get_weather import *

# ------------------------------------------------------------------------------------------------------------------------
def _generate_data_list(json_data):
    # 클래스 이름 정의
    class_names = ["class_INSURANCE", "class_BUSINESS", "class_ESG", "class_COMPLIANCE", 
                   "class_ORGANIZATION", "class_MARKET", "class_TECHINNOV", "class_SPORTS", "class_AD", "class_NO"]
    
    # 각 클래스별 연도별 값 리스트 생성 (연도 제외)
    data_list = []
    for class_name in class_names:
        # 각 연도별 해당 클래스의 값을 수집
        year_values = []
        for year_data in json_data:
            year_key = list(year_data.keys())[0]
            class_counts = year_data[year_key].get("class_counts", {})
            year_values.append(class_counts.get(class_name, 0))  # 클래스 값이 없으면 0 추가
        data_list.append(year_values)
    
    return data_list

# ------------------------------------------------------------------------------------------------------------------------
def _extract_year_data(_year, _data):
    class_keys = ["class_INSURANCE", "class_BUSINESS", "class_ESG", "class_COMPLIANCE", "class_ORGANIZATION", "class_MARKET", "class_TECHINNOV", "class_SPORTS", "class_AD", "class_NO"]
    # months = ["01월", "02월", "03월", "04월", "05월", "06월", "07월", "08월", "09월", "10월", "11월", "12월"]
    year_data = {class_name: [0] * 12 for class_name in class_keys}
    for entry in _data:
        for month, info in entry.items():
            entry_year, entry_month = month.split("-")
            if entry_year == _year:
                month_index = int(entry_month) - 1
                for class_name in class_keys:
                    year_data[class_name][month_index] = info["class_counts"].get(class_name, 0)
    # 각 클래스의 데이터를 역순으로 저장
    data_list = [year_data[class_name][::-1] for class_name in class_keys]
    return data_list

# ------------------------------------------------------------------------------------------------------------------------
def _get_total_articles(json_data, target_month):
    for month_data in json_data:
        if target_month in month_data:
            return month_data[target_month].get("total_articles", 0)  # 값이 없으면 0 반환
    return 0  # 대상 월이 없으면 0 반환

# ------------------------------------------------------------------------------------------------------------------------
def _get_all_articles(json_data, target_year):
    # JSON 데이터 탐색
    for year_data in json_data:
        if target_year in year_data:
            return year_data[target_year].get("total_articles", 0)  # 값이 없으면 0 반환
    return 0  # 대상 연도가 없으면 0 반환

# ------------------------------------------------------------------------------------------------------------------------
def _extract_monthly_data(_year_month, _json_data):
    class_keys = ["class_INSURANCE", "class_BUSINESS", "class_ESG", "class_COMPLIANCE", "class_ORGANIZATION", 
                  "class_MARKET", "class_TECHINNOV", "class_SPORTS", "class_AD", "class_NO"]
    class_data = {class_name: [0] * 31 for class_name in class_keys}
    for month_data in _json_data:
        for date, day_data in month_data.items():
            if date.startswith(_year_month):  # "년-월"에 해당하는 날짜만 추출
                day = int(date.split("-")[2]) - 1  # 일별 인덱스 (0부터 시작)
                for class_type, count in day_data["class_counts"].items():
                    if class_type in class_keys:  # 클래스 키에 해당하는 데이터만 업데이트
                        class_data[class_type][day] = count  # 해당 일에 카운트 데이터 추가

    # data_list 생성 (클래스명과 날짜 레이블 없이 일별 카운트만 포함)
    data_list = [class_data[class_type] for class_type in class_keys]  # 클래스명 없이 일별 카운트 배열만 추가
    return data_list

# ------------------------------------------------------------------------------------------------------------------------
def _get_total(json_data, target_date):
    for month_data in json_data:
        if target_date in month_data:
            total = month_data[target_date].get("total_articles", 0) 
            return total
    return 0

# ------------------------------------------------------------------------------------------------------------------------
def _get_news_agencies(json_data, target_date):
    for month_data in json_data:
        if target_date in month_data:
            news_agencies = month_data[target_date].get("news_agencies", {})
            sorted_news_agencies = dict(sorted(news_agencies.items(), key=lambda x: x[1], reverse=True))
            return sorted_news_agencies
    return {}

# ------------------------------------------------------------------------------------------------------------------------
def _get_bullets(json_data, target_date, class_type):
    for month_data in json_data:
        if target_date in month_data:
            summaries = month_data[target_date].get("summary_per_class", {})
            if class_type in summaries:
                return summaries[class_type][0].get("bullet", [])
    return []

# ------------------------------------------------------------------------------------------------------------------------
def _get_urls(json_data, target_date, class_type):
    for month_data in json_data:
        if target_date in month_data:
            urls = month_data[target_date].get("url_per_class", {})
            if class_type in urls:
                return urls[class_type]
    return []

# ------------------------------------------------------------------------------------------------------------------------
def _get_reasons(json_data, target_date, class_type):
    for month_data in json_data:
        if target_date in month_data:
            reasons = month_data[target_date].get("reason_per_class", {})
            if class_type in reasons:
                return reasons[class_type]
    return []


# ------------------------------------------------------------------------------------------------------------------------
def _get_hashtags(json_data, target_date, class_type):
    if class_type == 'class_MENTION':
        return []
    for month_data in json_data:
        if target_date in month_data:
            entities = month_data[target_date].get("entities_per_class", {})
            if class_type in entities:
                sorted_entities = dict(sorted(entities[class_type].items(), key=lambda x: x[1], reverse=True))
                return sorted_entities
    return []

# ------------------------------------------------------------------------------------------------------------------------
def _is_skip_date(_json_data, _target):
    for month_data in _json_data:
        if _target in month_data:
            return True
    return False

# ------------------------------------------------------------------------------------------------------------------------
def _is_skip_class(_json_data, _target, _class):
    for month_data in _json_data:
        if _target in month_data:
            urls = month_data[_target].get("class_counts", {})
            # return _class in urls
            if _class in urls:
                return True, urls[_class]  # True와 클래스 값 반환
    return False, None
# ------------------------------------------------------------------------------------------------------------------------
def all_dashboard_company2(_singer):

    # from streamlit_autorefresh import st_autorefresh
    #Time
    nowTime = datetime.now()
    current_time = nowTime.strftime("%H:%M:%S")
    today = str(date.today())
    # st.write(today)
    timeMetric,= st.columns(1)
    timeMetric.metric("",today)

    # Row A
    a1, a2, a3 = st.columns(3)
    # a1.image(logo)
    a2.metric("Stockholm Temperature", f"{11}", f"{22}"+"%")
    a3.metric("Stockholm time", current_time)


    # Row B
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Humidity", f"{get_humidity()}"+"%")
    b2.metric("Feels like", f"{get_feel()}")
    b3.metric("Highest temperature", f"{get_temp_max()}")
    b4.metric("Lowest temperature", f"{get_temp_min()}")

    # Row C
    #C1 being the graph, C2 The Table.
    c1, c2 = st.columns((7,3))

    #Graph:
    with c1:

        chart_data = pd.DataFrame(
            np.random.randn(20, 3),
            columns=['Low', 'High', 'Close'])
        st.line_chart(chart_data)

    #The fake nonsens table:
    with c2:
        df = pd.DataFrame(
            np.random.randn(7, 5),
            columns=('Paris','Malta','Stockholm','Peru','Italy')
        )

        st.table(df)

    #Manually refresh button
    st.button("Run me manually")


# ------------------------------------------------------------------------------------------------------------------------
def all_dashboard_company(_company):
    st.subheader(f'분석할 회사 : {_company}')
    # with st.expander('분류기준 설명'):
    #     st.write('- INSURANCE : 삼성생명의 금융 상품이나 보험 상품에 관한 내용')
    #     st.write('- BUSINESS : 삼성생명의 경영 활동이나 실적과 관련된 내용')
    #     st.write('- ESG : 삼성생명의 사회적 책임 활동이나 ESG(환경, 사회, 지배구조)와 관련된 내용')
    #     st.write('- COMPLIANCE : 삼성생명과 관련된 법적 문제나 규제 이슈에 대한 내용')
    #     st.write('- ORGANIZATION : 삼성생명의 인사 이동이나 조직 개편과 관련된 내용')
    #     st.write('- MARKET : 삼성생명의 보험 및 금융 시장에서의 위치나 경쟁 상황과 관련된 내용')
    #     st.write('- TECHINNOV : 삼성생명의 기술 혁신이나 디지털 전환과 관련된 내용')
    #     st.write('- SPORTS : 삼성생명 소속 스포츠 구단이나, 스포츠 육성 및 저변확대에 관련된 내용')
    #     st.write('- AD : 삼성생명의 광고 캠페인이나 홍보 활동과 관련된 내용')
    #     st.write('- NO : 삼성생명과 관련된 특정 카테고리에 포함되지 않는 내용')

    tab1, tab2 = st.tabs(["설명", "분류기준 설명"])

    with tab1:
        st.markdown(f"<h4><span style='font-size:20px;'>설명</span></h4>", unsafe_allow_html=True)
        st.write('2020 부터 현재까지의 "삼성생명"에 대한 언론뉴스를 모두 모아, llm 을 통한 통계, 분석, 요약, 키워드추출 수행')

    with tab2:
        st.markdown(f"<h4><span style='font-size:20px;'>분류기준</span></h4>", unsafe_allow_html=True)
        st.write('- **INSURANCE** : 삼성생명의 금융 상품이나 보험 상품에 관한 내용')
        st.write('- **BUSINESS** : 삼성생명의 경영 활동이나 실적과 관련된 내용')
        st.write('- **ESG** : 삼성생명의 사회적 책임 활동이나 ESG(환경, 사회, 지배구조)와 관련된 내용')
        st.write('- **COMPLIANCE** : 삼성생명과 관련된 법적 문제나 규제 이슈에 대한 내용')
        st.write('- **ORGANIZATION** : 삼성생명의 인사 이동이나 조직 개편과 관련된 내용')
        st.write('- **MARKET** : 삼성생명의 보험 및 금융 시장에서의 위치나 경쟁 상황과 관련된 내용')
        st.write('- **TECHINNOV** : 삼성생명의 기술 혁신이나 디지털 전환과 관련된 내용')
        st.write('- **SPORTS** : 삼성생명 소속 스포츠 구단이나, 스포츠 육성 및 저변확대에 관련된 내용')
        st.write('- **AD** : 삼성생명의 광고 캠페인이나 홍보 활동과 관련된 내용')
        st.write('- **NO** : 삼성생명과 관련된 특정 카테고리에 포함되지 않는 내용')

    st.divider()



    fmname = f'./jsondata/year_{_company}.json'
    with open(fmname, "r", encoding="utf-8") as file:
        year_data = json.load(file)

    data_list = _generate_data_list(year_data)
    names = SX_CLASS_NAME
    series = all_series(names, data_list)
    options = all_company_option(series)

    if 'legend_selected' not in st.session_state:
        st.session_state['legend_selected'] = {name: True for name in names}
    options['legend']['selected'] = st.session_state['legend_selected']
    options['legend']['textStyle'] = {
        'color': 'gray',  # 원하는 색상으로 변경하세요
        'fontSize': 14,  # 옵션: 글자 크기 설정
        # 'fontWeight': 'bold',  # 옵션: 글자 두께 설정
    }
    events = {
        "click": "function(params) { return [params.type, params.name, params.value, "
                 "params.componentType, params.seriesType, params.seriesIndex, params.seriesName, "
                 "params.dataIndex, params.dataType, params.data, params.color, params.info ]}",
        "legendselectchanged": "function(params) { return ['legendselectchanged', params.selected]; }",
    }
    st.success('자세히 보기를 원하는 "년도"를 클릭하세요', icon="✅")
    # Adjust the columns to align buttons as desired
    spacer_col, clear_col, all_col = st.columns([0.43, 0.05, 0.52], gap="small")
    with all_col:
        if st.button("clear", key="key_all_button11"):
            options['legend']['selected'] = {name: False for name in names}
            st.session_state['legend_selected'] = options['legend']['selected']
            # Reset main_dashboard display flag
            st.session_state['show_main_dashboard'] = False  # Only reset show_main_dashboard
    with clear_col:
        if st.button("all", key="key_all_button1"):
            options['legend']['selected'] = {name: True for name in names}
            st.session_state['legend_selected'] = options['legend']['selected']
            # Reset main_dashboard display flag
            st.session_state['show_main_dashboard'] = False  # Only reset show_main_dashboard


    s = st_echarts(options=options, events=events, height="500px", key="key_all_dashboard")
    st.divider()

    if s is not None:
        if s[0] == 'legendselectchanged':
            st.session_state['legend_selected'] = s[1]
            # Reset main_dashboard display flag
            st.session_state['show_main_dashboard'] = False
        else:
            xx = s[1].replace("년", "").strip()
            susu = _get_all_articles(year_data, xx)
            year_dashboard(_company, xx, susu)
    else:
        st.session_state['legend_selected'] = options['legend']['selected']

# ------------------------------------------------------------------------------------------------------------------------
def year_dashboard(_company, _selected_year, susu):
    head = f'{_selected_year}년'
    st.markdown(f"<h3>{head} - <span style='font-size:20px;'>( 전체 기사수 {susu} 개 )</span></h3>", unsafe_allow_html=True)
    names = SX_CLASS_NAME
    fmname = f'./jsondata/month_{_company}.json'
    with open(fmname, "r", encoding="utf-8") as file:
        month_data = json.load(file)

    data_list = _extract_year_data(_selected_year, month_data)
    series = year_series(names, data_list)
    options = year_company_option(series)

    options['legend']['selected'] = st.session_state.get('legend_selected', {name: True for name in names})
    options['legend']['textStyle'] = {
        'color': 'gray',  # 원하는 색상으로 변경하세요
        'fontSize': 14,  # 옵션: 글자 크기 설정
        # 'fontWeight': 'bold',  # 옵션: 글자 두께 설정
    }
    events = {
        "click": "function(params) { return [params.type, params.name, params.value, "
                 "params.componentType, params.seriesType, params.seriesIndex, params.seriesName, "
                 "params.dataIndex, params.dataType, params.data, params.color, params.info ]}",
        "legendselectchanged": "function(params) { return ['legendselectchanged', params.selected]; }",
    }

    st.success('자세히 보기를 원하는 "월"을 클릭하세요', icon="✅")
    s = st_echarts(options=options, events=events, height="500px", key="key_year_dashboard")
    st.divider()

    if s is not None:
        if s[0] == 'legendselectchanged':
            st.session_state['legend_selected'] = s[1]
            # Reset main_dashboard display flag
            st.session_state['show_main_dashboard'] = False
        else:
            xx = s[1].replace("월", "").strip()
            susu = _get_total_articles(month_data, f'{_selected_year}-{xx}')
            month_dashboard(_company, susu, _selected_year, s[1])
    else:
        st.session_state['legend_selected'] = options['legend']['selected']

# ------------------------------------------------------------------------------------------------------------------------
def month_dashboard(_company, susu, _selected_year, _month):
    head = f'{_selected_year}년 {_month}'
    st.markdown(f"<h3>{head} - <span style='font-size:20px;'>( 전체 기사수 {susu} 개 )</span></h3>", unsafe_allow_html=True)
    names = SX_CLASS_NAME
    fdname = f'./jsondata/day_{_company}_{_selected_year}.json'
    with open(fdname, "r", encoding="utf-8") as file:
        day_data = json.load(file)
    ynname = head.replace("년 ", "-").replace("월", "").strip()
    data_list = _extract_monthly_data(ynname, day_data)
    series = month_series(names, data_list)
    options = month_company_option(series)
    options['legend']['selected'] = st.session_state.get('legend_selected', {name: True for name in names})
    options['legend']['textStyle'] = {
        'color': 'gray',  # 원하는 색상으로 변경하세요
        'fontSize': 14,  # 옵션: 글자 크기 설정
        # 'fontWeight': 'bold',  # 옵션: 글자 두께 설정
    }
    eventsx = {
        "click": "function(params) { return [params.type, params.name, params.value, "
                 "params.componentType, params.seriesType, params.seriesIndex, params.seriesName, "
                 "params.dataIndex, params.dataType, params.data, params.color, params.info ]}",
        "legendselectchanged": "function(params) { return ['legendselectchanged', params.selected]; }",
    }

    st.success('자세히 보기를 원하는 "날짜"를 클릭하세요', icon="✅")
    s = st_echarts(options=options, events=eventsx, height="500px", key="key_month_dashboard")
    st.divider()

    # Initialize show_main_dashboard flag if not present
    if 'show_main_dashboard' not in st.session_state:
        st.session_state['show_main_dashboard'] = False

    if s is not None:
        if s[0] == 'legendselectchanged':
            st.session_state['legend_selected'] = s[1]
            # Reset main_dashboard display flag
            st.session_state['show_main_dashboard'] = False
        else:
            head = f'{head} {s[1]}'
            st.session_state['day_head'] = head
            st.session_state['company'] = _company
            st.session_state['day_data'] = day_data
            st.session_state['show_main_dashboard'] = True  # Set flag to display main_dashboard
    else:
        st.session_state['legend_selected'] = options['legend']['selected']

    # Display main_dashboard if flag is True
    if st.session_state.get('show_main_dashboard', False):
        st.subheader(st.session_state['day_head'])
        day_dashboard(st.session_state['company'], st.session_state['day_data'], st.session_state['day_head'])

# ------------------------------------------------------------------------------------------------------------------------
def day_dashboard(_company, day_data, _head):
    dname = _head.replace("년 ", "-").replace("월 ", "-").replace("일", "").strip()
    if not _is_skip_date(day_data, dname):
        return
    except_mention = [name for name in SX_CLASS_NAME if name != "MENTION"]
    class_counts = []
    for _cidx in except_mention:
        is_skip, class_count = _is_skip_class(day_data, dname, f'class_{_cidx}')
        if is_skip:
            class_counts.append((_cidx, class_count))

    selected_classes = [name for name, selected in st.session_state.get('legend_selected', {}).items() if selected]
    sorted_classes = sorted(
        [item for item in class_counts if item[0] in selected_classes],
        key=lambda x: x[1], reverse=True
    )
    for _cidx, class_count in sorted_classes:
        class_dashboard(day_data, dname, _cidx)

    if "MENTION" in selected_classes:
        class_dashboard(day_data, dname, "MENTION")

    st.info('NEWS AGENCIES')
    agency_list = _get_news_agencies(day_data, dname)
    with st.expander("언론사 리스트:"):
        for key, value in agency_list.items():
            st.write(f'{key} ({value})')
    st.divider()

# ------------------------------------------------------------------------------------------------------------------------
def class_dashboard(day_data, _dname, _class):
    is_skip, class_count = _is_skip_class(day_data, _dname, f'class_{_class}')
    if not is_skip:
        return

    total = _get_total(day_data, _dname)
    st.info(f'**{_class} ( {class_count} 개 / 총 {total} )**')

    #####################################################################
    hashtags = _get_hashtags(day_data, _dname, f'class_{_class}')
    if hashtags:
        def generate_annotated_text(_data):
            annotations = []
            for key, value in _data.items():
                annotations.append(annotation(key, f"({value})", font_family="Comic Sans MS", border="2px red"))
                annotations.append("  ")
            if annotations:
                annotations.pop()
            annotated_text(*annotations)
        generate_annotated_text(hashtags)

    #####################################################################
    summary_list = _get_bullets(day_data, _dname, f'class_{_class}')
    with st.expander("SUMMARY:"):
        for _idx in summary_list:
            st.code(_idx)

    #####################################################################
    url_list = _get_urls(day_data, _dname, f'class_{_class}')
    # with st.expander("URLS:"):
    #     for _idx in url_list:
    #         st.write(_idx)

    reason_list = _get_reasons(day_data, _dname, f'class_{_class}')
    with st.expander("URLS:"):
        for idx, url in enumerate(url_list):
            # Create a unique key for each URL button by including class and date
            key = f"url_{_class}_{_dname}_{idx}"
            if key not in st.session_state:
                st.session_state[key] = False

            # Create columns for the URL and the button
            cols = st.columns([0.85, 0.15])
            with cols[0]:
                st.write(url)
            with cols[1]:
                # Button with a unique key
                if st.button("요약 정리", key=f"show_button_{_class}_{_dname}_{idx}"):
                    st.session_state[key] = not st.session_state[key]

            # Display 'hello' if the button has been clicked
            if st.session_state[key]:
                st.write(reason_list[idx])

    st.divider()

# eof
