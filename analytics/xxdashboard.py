import json
import streamlit as st
from streamlit_echarts import st_echarts
from .chart_options import year_option, year_series, month_option, month_series, all_option, all_series
from annotated_text import annotated_text, annotation, parameters
from collections import defaultdict

SX_CLASS_NAME = ["MENTION", "BAD", "GOOD", "MUSIC", "ENT", "CONTRACT", "AD", "RIP", "NO"]

# ------------------------------------------------------------------------------------------------------------------------
def generate_data_list(json_data):
    class_names = ["class_MENTION", "class_BAD", "class_GOOD", "class_MUSIC",
                   "class_ENT", "class_CONTRACT", "class_AD", "class_RIP", "class_NO"]

    data_list = []
    for class_name in class_names:
        year_values = []
        for year_data in json_data:
            year_key = list(year_data.keys())[0]
            class_counts = year_data[year_key].get("class_counts", {})
            year_values.append(class_counts.get(class_name, 0))
        data_list.append(year_values)

    return data_list

# ------------------------------------------------------------------------------------------------------------------------
def _extract_year_data(_year, _data):
    class_keys = ["class_MENTION", "class_BAD", "class_GOOD", "class_MUSIC", "class_ENT",
                  "class_CONTRACT", "class_AD", "class_RIP", "class_NO"]
    year_data = {class_name: [0] * 12 for class_name in class_keys}
    for entry in _data:
        for month, info in entry.items():
            entry_year, entry_month = month.split("-")
            if entry_year == _year:
                month_index = int(entry_month) - 1
                for class_name in class_keys:
                    year_data[class_name][month_index] = info["class_counts"].get(class_name, 0)
    data_list = [year_data[class_name][::-1] for class_name in class_keys]
    return data_list

# ------------------------------------------------------------------------------------------------------------------------
def _get_total_articles(json_data, target_month):
    for month_data in json_data:
        if target_month in month_data:
            return month_data[target_month].get("total_articles", 0)
    return 0

# ------------------------------------------------------------------------------------------------------------------------
def _get_all_articles(json_data, target_year):
    for year_data in json_data:
        if target_year in year_data:
            return year_data[target_year].get("total_articles", 0)
    return 0

# ------------------------------------------------------------------------------------------------------------------------
def all_dashboard(_singer):
    st.subheader(f'가수 : {_singer}')
    fmname = f'./jsondata/year_{_singer}.json'
    with open(fmname, "r", encoding="utf-8") as file:
        year_data = json.load(file)

    data_list = generate_data_list(year_data)
    names = SX_CLASS_NAME
    series = all_series(names, data_list)
    options = all_option(series)

    if 'legend_selected' not in st.session_state:
        st.session_state['legend_selected'] = {name: True for name in names}
    options['legend']['selected'] = st.session_state['legend_selected']
    events = {
        "click": "function(params) { return [params.type, params.name, params.value, "
                 "params.componentType, params.seriesType, params.seriesIndex, params.seriesName, "
                 "params.dataIndex, params.dataType, params.data, params.color, params.info ]}",
        "legendselectchanged": "function(params) { return ['legendselectchanged', params.selected]; }",
    }

    # Adjust the columns to align buttons as desired
    spacer_col, clear_col, all_col = st.columns([0.43, 0.05, 0.52], gap="small")
    with all_col:
        if st.button("clear", key="key_all_button11"):
            options['legend']['selected'] = {name: False for name in names}
            st.session_state['legend_selected'] = options['legend']['selected']
            # Clear lower-level charts
            st.session_state['show_year_dashboard'] = False
            st.session_state['show_month_dashboard'] = False
            st.session_state['show_main_dashboard'] = False
    with clear_col:
        if st.button("all", key="key_all_button1"):
            options['legend']['selected'] = {name: True for name in names}
            st.session_state['legend_selected'] = options['legend']['selected']
            # Clear lower-level charts
            st.session_state['show_year_dashboard'] = False
            st.session_state['show_month_dashboard'] = False
            st.session_state['show_main_dashboard'] = False

    st.success('자세히 보기를 원하는 "년도"를 클릭하세요', icon="✅")
    s = st_echarts(options=options, events=events, height="500px", key="key_all_dashboard")
    st.divider()

    if 'show_year_dashboard' not in st.session_state:
        st.session_state['show_year_dashboard'] = False

    if s is not None:
        if s[0] == 'legendselectchanged':
            st.session_state['legend_selected'] = s[1]
            # Clear lower-level charts when legend changes
            st.session_state['show_year_dashboard'] = False
            st.session_state['show_month_dashboard'] = False
            st.session_state['show_main_dashboard'] = False
        else:
            xx = s[1].replace("년", "").strip()
            susu = _get_all_articles(year_data, xx)
            st.session_state['selected_year'] = xx
            st.session_state['singer'] = _singer
            st.session_state['susu'] = susu
            st.session_state['show_year_dashboard'] = True
    else:
        st.session_state['legend_selected'] = options['legend']['selected']

    # Display year_dashboard if needed
    if st.session_state.get('show_year_dashboard', False):
        year_dashboard(st.session_state['singer'], st.session_state['selected_year'], st.session_state['susu'])

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
    options = year_option(series)

    options['legend']['selected'] = st.session_state.get('legend_selected', {name: True for name in names})
    events = {
        "click": "function(params) { return [params.type, params.name, params.value, "
                 "params.componentType, params.seriesType, params.seriesIndex, params.seriesName, "
                 "params.dataIndex, params.dataType, params.data, params.color, params.info ]}",
        "legendselectchanged": "function(params) { return ['legendselectchanged', params.selected]; }",
    }
    st.success('자세히 보기를 원하는 "월"을 클릭하세요', icon="✅")
    s = st_echarts(options=options, events=events, height="500px", key="key_year_dashboard")
    st.divider()

    if 'show_month_dashboard' not in st.session_state:
        st.session_state['show_month_dashboard'] = False

    if s is not None:
        if s[0] == 'legendselectchanged':
            st.session_state['legend_selected'] = s[1]
            # Clear lower-level charts when legend changes
            st.session_state['show_month_dashboard'] = False
            st.session_state['show_main_dashboard'] = False
        else:
            xx = s[1].replace("월", "").strip()
            susu = _get_total_articles(month_data, f'{_selected_year}-{xx}')
            st.session_state['selected_month'] = s[1]
            st.session_state['susu_month'] = susu
            st.session_state['year_head'] = head
            st.session_state['singer'] = _singer
            st.session_state['show_month_dashboard'] = True
    else:
        st.session_state['legend_selected'] = options['legend']['selected']

    if st.session_state.get('show_month_dashboard', False):
        month_dashboard(st.session_state['singer'], st.session_state['susu_month'],
                        st.session_state['year_head'], st.session_state['selected_month'])

# ------------------------------------------------------------------------------------------------------------------------
def _extract_monthly_data(_year_month, _json_data):
    class_keys = ["class_MENTION", "class_BAD", "class_GOOD", "class_MUSIC", "class_ENT",
                  "class_CONTRACT", "class_AD", "class_RIP", "class_NO"]
    class_data = {class_name: [0] * 31 for class_name in class_keys}
    for month_data in _json_data:
        for date, day_data in month_data.items():
            if date.startswith(_year_month):
                day = int(date.split("-")[2]) - 1
                for class_type, count in day_data["class_counts"].items():
                    if class_type in class_keys:
                        class_data[class_type][day] = count
    data_list = [class_data[class_type] for class_type in class_keys]
    return data_list

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
    options = month_option(series)
    options['legend']['selected'] = st.session_state.get('legend_selected', {name: True for name in names})
    eventsx = {
        "click": "function(params) { return [params.type, params.name, params.value, "
                 "params.componentType, params.seriesType, params.seriesIndex, params.seriesName, "
                 "params.dataIndex, params.dataType, params.data, params.color, params.info ]}",
        "legendselectchanged": "function(params) { return ['legendselectchanged', params.selected]; }",
    }
    st.success('자세히 보기를 원하는 "날짜"를 클릭하세요', icon="✅")
    s = st_echarts(options=options, events=eventsx, height="500px", key="key_month_dashboard")
    st.divider()

    if 'show_main_dashboard' not in st.session_state:
        st.session_state['show_main_dashboard'] = False

    if s is not None:
        if s[0] == 'legendselectchanged':
            st.session_state['legend_selected'] = s[1]
            # Clear main dashboard when legend changes
            st.session_state['show_main_dashboard'] = False
        else:
            head = f'{head} {s[1]}'
            st.subheader(head)
            st.session_state['singer'] = _singer
            st.session_state['day_data'] = day_data
            st.session_state['head'] = head
            st.session_state['show_main_dashboard'] = True
    else:
        st.session_state['legend_selected'] = options['legend']['selected']

    if st.session_state.get('show_main_dashboard', False):
        main_dashboard(st.session_state['singer'], st.session_state['day_data'], st.session_state['head'])

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
            if _class in urls:
                return True, urls[_class]
        return False, None

# ------------------------------------------------------------------------------------------------------------------------
def main_dashboard(_singer, day_data, _head):
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
        day_dashboard(_singer, day_data, dname, _cidx)

    if "MENTION" in selected_classes:
        day_dashboard(_singer, day_data, dname, "MENTION")

    st.info('NEWS AGENCIES')
    agency_list = _get_news_agencies(day_data, dname)
    with st.expander("언론사 리스트:"):
        for key, value in agency_list.items():
            st.write(f'{key} ({value})')
    st.divider()

# ------------------------------------------------------------------------------------------------------------------------
def day_dashboard(_singer, day_data, _dname, _class):
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
    with st.expander("URLS:"):
        for _idx in url_list:
            st.write(_idx)

    st.divider()

# eof
