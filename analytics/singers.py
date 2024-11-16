from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts

from .dashboard_news import all_dashboard_news


ST_SINGER = {
    # 페이지 옵션으로 뜨는 부분


    "god": (
        all_dashboard_news,
        ["2020", "2021", "2022", "2023", "2024"],
    ),
    "이루": (
        all_dashboard_news,
        ["2020", "2021", "2022", "2023", "2024"],
    ),
    "진민호": (
        all_dashboard_news,
        ["2020", "2021", "2022", "2023", "2024"],
    ),
    "휘성": (
        all_dashboard_news,
        ["2020", "2021", "2022", "2023", "2024"],
    )
}


# def render_basic_bar():
#     options = {
#         "xAxis": {
#             "type": "category",
#             "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
#         },
#         "yAxis": {"type": "value"},
#         "series": [{"data": [120, 200, 150, 80, 70, 110, 130], "type": "bar"}],
#     }
#     st_echarts(options=options, height="500px")


# def render_set_style_of_single_bar():
#     options = {
#         "xAxis": {
#             "type": "category",
#             "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
#         },
#         "yAxis": {"type": "value"},
#         "series": [
#             {
#                 "data": [
#                     120,
#                     {"value": 200, "itemStyle": {"color": "#a90000"}},
#                     150,
#                     80,
#                     70,
#                     110,
#                     130,
#                 ],
#                 "type": "bar",
#             }
#         ],
#     }
#     st_echarts(
#         options=options,
#         height="400px",
#     )


