from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts

from .dashboard_news import all_dashboard_news
from .dashboard_company import all_dashboard_company

ST_COMPANY = {
    # 페이지 옵션으로 뜨는 부분


    "삼성생명": (
        all_dashboard_company,
        ["2020", "2021"],
    ),

}