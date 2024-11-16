import os
import json
import streamlit as st
from streamlit_echarts import st_echarts
from .chart_options import year_news_option, year_series, month_news_option, month_series, all_news_option, all_series
from annotated_text import annotated_text, annotation, parameters
from collections import defaultdict
# class_SOCIAL, class_ILLEGAL, class_CONTRACT, class_ENT, class_SAJAEGI, class_MUSIC, class_AD, class_RIP, class_AWARD, class_NO
SX_CLASS_NAME = ["SOCIAL", "ILLEGAL", "CONTRACT", "ENT", "SAJAEGI", "MUSIC", "AD", "RIP", "AWARD", "NO"]

os.environ["STREAMLIT_THEME_BASE"] = "dark"

# ------------------------------------------------------------------------------------------------------------------------
def _generate_data_list(json_data):
    # 클래스 이름 정의
    class_names = ["class_SOCIAL", "class_ILLEGAL", "class_CONTRACT", "class_ENT", "class_SAJAEGI", "class_MUSIC", "class_AD", "class_RIP", "class_AWARD", "class_NO"]
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
    class_keys = ["class_SOCIAL", "class_ILLEGAL", "class_CONTRACT", "class_ENT", "class_SAJAEGI", "class_MUSIC", "class_AD", "class_RIP", "class_AWARD", "class_NO"]
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
    class_keys = ["class_SOCIAL", "class_ILLEGAL", "class_CONTRACT", "class_ENT", "class_SAJAEGI", "class_MUSIC", "class_AD", "class_RIP", "class_AWARD", "class_NO"]
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
def all_dashboard_news(_singer):
    st.subheader(f'분석할 가수 : "{_singer}"')
    fmname = f'./jsondata/year_{_singer}.json'
    with open(fmname, "r", encoding="utf-8") as file:
        year_data = json.load(file)

    data_list = _generate_data_list(year_data)
    names = SX_CLASS_NAME
    series = all_series(names, data_list)
    options = all_news_option(series)

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
    st.divider()
    st.success('자세히 보기를 원하는 "년도"를 클릭하세요', icon="📌")
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
            year_dashboard(_singer, xx, susu)
    else:
        st.session_state['legend_selected'] = options['legend']['selected']

# ------------------------------------------------------------------------------------------------------------------------
def year_dashboard(_singer, _selected_year, susu):
    head = f'{_selected_year}년'
    st.markdown(f"<h3>{head} - <span style='font-size:20px;'>( 전체 기사수 {susu} 개 )</span></h3>", unsafe_allow_html=True)
    names = SX_CLASS_NAME
    fmname = f'./jsondata/month_{_singer}.json'
    with open(fmname, "r", encoding="utf-8") as file:
        month_data = json.load(file)

    data_list = _extract_year_data(_selected_year, month_data)
    series = year_series(names, data_list)
    options = year_news_option(series)

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

    st.success('자세히 보기를 원하는 "월"을 클릭하세요', icon="📌")
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
            month_dashboard(_singer, susu, head, s[1])
    else:
        st.session_state['legend_selected'] = options['legend']['selected']

# ------------------------------------------------------------------------------------------------------------------------
def month_dashboard(_singer, susu, _year, _month):
    head = f'{_year} {_month}'
    st.markdown(f"<h3>{head} - <span style='font-size:20px;'>( 전체 기사수 {susu} 개 )</span></h3>", unsafe_allow_html=True)
    names = SX_CLASS_NAME
    fdname = f'./jsondata/day_{_singer}.json'
    with open(fdname, "r", encoding="utf-8") as file:
        day_data = json.load(file)
    ynname = head.replace("년 ", "-").replace("월", "").strip()
    data_list = _extract_monthly_data(ynname, day_data)
    series = month_series(names, data_list)
    options = month_news_option(series)
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

    st.success('자세히 보기를 원하는 "날짜"를 클릭하세요', icon="📌")
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
            st.session_state['singer'] = _singer
            st.session_state['day_data'] = day_data
            st.session_state['show_main_dashboard'] = True  # Set flag to display main_dashboard
    else:
        st.session_state['legend_selected'] = options['legend']['selected']

    # Display main_dashboard if flag is True
    if st.session_state.get('show_main_dashboard', False):
        st.subheader(st.session_state['day_head'])
        day_dashboard(st.session_state['singer'], st.session_state['day_data'], st.session_state['day_head'])

# ------------------------------------------------------------------------------------------------------------------------
def day_dashboard(_singer, day_data, _head):
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
        class_dashboard(_singer, day_data, dname, _cidx)

    if "MENTION" in selected_classes:
        class_dashboard(_singer, day_data, dname, "MENTION")

    st.error('NEWS AGENCIES', icon="📄")
    agency_list = _get_news_agencies(day_data, dname)
    with st.expander(f"\"{_head}\" 에 위 기사들을 게재한 언론사 리스트:"):
        for key, value in agency_list.items():
            st.write(f'{key} ({value})')
    st.divider()


# ------------------------------------------------------------------------------------------------------------------------
def _get_reasons(json_data, target_date, class_type):
    for month_data in json_data:
        if target_date in month_data:
            reasons = month_data[target_date].get("reason_per_class", {})
            if class_type in reasons:
                return reasons[class_type]
    return []


# ------------------------------------------------------------------------------------------------------------------------
def class_dashboard(_singer, day_data, _dname, _class):
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

    # with st.expander("URLS:"):
    #     for idx, url in enumerate(url_list):
    #         # Unique key for each URL to manage its state
    #         key = f"url_{idx}"
    #         if key not in st.session_state:
    #             st.session_state[key] = False

    #         # Create columns for the URL label and the button
    #         cols = st.columns([0.85, 0.15])
    #         with cols[0]:
    #             st.write(f"URL {idx+1}")
    #             # st.write(key)
    #         with cols[1]:
    #             # Button to toggle the display of the URL
    #             if st.button("Show", key=f"show_button_{idx}"):
    #                 st.session_state[key] = not st.session_state[key]

    #         # Display the URL if the button has been clicked
    #         if st.session_state[key]:
    #             st.code(url)


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
                if st.button("의견 보기", key=f"show_button_{_class}_{_dname}_{idx}"):
                    st.session_state[key] = not st.session_state[key]

            # Display 'hello' if the button has been clicked
            if st.session_state[key]:
                st.write(reason_list[idx])













    st.divider()

# eof