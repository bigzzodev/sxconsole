# ["class_SOCIAL", "class_ILLEGAL", "class_CONTRACT", "class_ENT", "class_SAJAEGI", "class_MUSIC", "class_AD", "class_RIP", "class_AWARD", "class_NO"]
# ------------------------------------------------------------------------------------------------------------------------
def all_news_option(_series):
    options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {
            "data": ["SOCIAL", "ILLEGAL", "CONTRACT", "ENT", "SAJAEGI", "MUSIC", "AD", "RIP", "AWARD", "NO"],
            "textStyle": {"color": "white"},
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "value"},
        "yAxis": {
            "type": "category",
            "data": ["2020년", "2021년", "2022년", "2023년", "2024년"],
        }
    }
    options["series"] = _series
    return options

# ------------------------------------------------------------------------------------------------------------------------
def all_company_option(_series):
    options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {
            "data": ["INSURANCE", "BUSINESS", "ESG", "COMPLIANCE", "ORGANIZATION", "MARKET", "TECHINNOV", "SPORTS", "AD", "NO"],
            "textStyle": {"color": "white"},
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "value"},
        "yAxis": {
            "type": "category",
            "data": ["2020년", "2021년", "2022년", "2023년", "2024년"],
        }
    }
    options["series"] = _series
    return options
# [
#     {
#         "2020": {
#             "total_articles": 2250,
#             "class_counts": {
#                 "class_MENTION": 1173,
#                 "class_BAD": 22,
#                 "class_GOOD": 32,
#                 "class_MUSIC": 223,
#                 "class_ENT": 712,
#                 "class_CONTRACT": 33,
#                 "class_AD": 12,
#                 "class_RIP": 0,
#                 "class_NO": 43
#             }
#         }
#     },
#     {
#         "2021": {
#             "total_articles": 2523,
#             "class_counts": {
#                 "class_MENTION": 1187,
#                 "class_BAD": 12,
#                 "class_GOOD": 150,
#                 "class_MUSIC": 171,
#                 "class_ENT": 942,
#                 "class_CONTRACT": 22,
#                 "class_AD": 3,
#                 "class_RIP": 1,
#                 "class_NO": 35
#             }
#         }
#     },
#     {
#         "2022": {
#             "total_articles": 2805,
#             "class_counts": {
#                 "class_MENTION": 829,
#                 "class_BAD": 14,
#                 "class_GOOD": 81,
#                 "class_MUSIC": 490,
#                 "class_ENT": 1291,
#                 "class_CONTRACT": 69,
#                 "class_AD": 10,
#                 "class_RIP": 0,
#                 "class_NO": 21
#             }
#         }
#     },
# 이런식의 json 오브젝트를 받아서, 아래와 같은 이중 리스트 반환하는 함수 만들어
# MENTION, BAD, 2024년, 등등은 주석임, 

#     data_list = [
#              2024년   2023년  2022년  2021년 2020년  
#     MENTION  [100,    302,    301,   334,   390],
#     BAD      [555,    132,    101,   134,   901],
#     GOOD     [100,    182,    191,   234,   290],
#     MUSIC    [150,    212,    201,   154,   190],
#     ENT      [820,    832,    901,   934,   129],
#     CONTRACT [820,    832,    901,   934,   129],
#     AD       [120,    132,    101,   134,   910],
#     RIP      [120,    132,    101,   134,   910],
#     NO       [120,    132,    101,   134,   910]
#     ]


# ------------------------------------------------------------------------------------------------------------------------
def all_series(_names, _data_list):
    series = []
    for name, data in zip(_names, _data_list):
        item = {
            "name": name,
            "type": "bar",
            "stack": "total",
            "label": {"show": True},
            "emphasis": {"focus": "series"},
            "data": data
        }
        series.append(item)
    return series

# ------------------------------------------------------------------------------------------------------------------------
def year_news_option(_series):
    options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {
            "data": ["SOCIAL", "ILLEGAL", "CONTRACT", "ENT", "SAJAEGI", "MUSIC", "AD", "RIP", "AWARD", "NO"],
            "textStyle": {"color": "white"},
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "value"},
        "yAxis": {
            "type": "category",
            "data": ["12월", "11월", "10월", "09월", "08월", "07월", "06월", "05월", "04월", "03월", "02월", "01월"],
        }
    }
    options["series"] = _series
    return options

# ------------------------------------------------------------------------------------------------------------------------
def year_company_option(_series):
    options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {
            "data": ["INSURANCE", "BUSINESS", "ESG", "COMPLIANCE", "ORGANIZATION", 'MARKET', 'TECHINNOV', 'SPORTS', 'AD', 'NO'],
            "textStyle": {"color": "white"},
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "value"},
        "yAxis": {
            "type": "category",
            "data": ["12월", "11월", "10월", "09월", "08월", "07월", "06월", "05월", "04월", "03월", "02월", "01월"],
        }
    }
    options["series"] = _series
    return options


# ------------------------------------------------------------------------------------------------------------------------
def year_series(_names, _data_list):
    series = []
    for name, data in zip(_names, _data_list):
        item = {
            "name": name,
            "type": "bar",
            "stack": "total",
            "label": {"show": True},
            "emphasis": {"focus": "series"},
            "data": data
        }
        series.append(item)
    return series

# ------------------------------------------------------------------------------------------------------------------------
def month_news_option(_series):
    options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {
            "data": ["SOCIAL", "ILLEGAL", "CONTRACT", "ENT", "SAJAEGI", "MUSIC", "AD", "RIP", "AWARD", "NO"],
            "textStyle": {"color": "white"},
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "yAxis": {"type": "value"},
        "xAxis": {
            "type": "category",
            "data": ["01일", "02일", "03일", "04일", "05일", "06일", "07일", "08일", "09일", "10일", "11일", "12일", "13일", "14일", "15일", "16일", "17일", "18일", "19일", "20일", "21일", "22일", "23일", "24일", "25일", "26일", "27일", "28일", "29일", "30일", "31일"]
        }
    }
    options["series"] = _series
    return options

# ------------------------------------------------------------------------------------------------------------------------
def month_company_option(_series):
    options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {
            "data": ["INSURANCE", "BUSINESS", "ESG", "COMPLIANCE", "ORGANIZATION", 'MARKET', 'TECHINNOV', 'SPORTS', 'AD', 'NO'],
            "textStyle": {"color": "white"},
        },
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "yAxis": {"type": "value"},
        "xAxis": {
            "type": "category",
            "data": ["01일", "02일", "03일", "04일", "05일", "06일", "07일", "08일", "09일", "10일", "11일", "12일", "13일", "14일", "15일", "16일", "17일", "18일", "19일", "20일", "21일", "22일", "23일", "24일", "25일", "26일", "27일", "28일", "29일", "30일", "31일"]
        }
    }
    options["series"] = _series
    return options

# ------------------------------------------------------------------------------------------------------------------------
def month_series(_names, _data_list):
    series = []
    for name, data in zip(_names, _data_list):
        item = {
            "name": name,
            "type": "bar",
            "stack": "total",
            "label": {"show": True},
            "emphasis": {"focus": "series"},
            "data": data
        }
        series.append(item)
    return series

































# ------------------------------------------------------------------------------------------------------------------------
            # {
            #     "name": "MENTION",
            #     "type": "bar",
            #     "stack": "total",
            #     "label": {"show": False},
            #     "emphasis": {"focus": "series"},
            #     "data": [555, 302, 301, 334, 390, 330, 320, 301, 334, 390, 88, 99, 555, 302, 301, 334, 390, 330, 320, 301, 334, 390, 88, 99, 390, 330, 320, 301, 334, 390, 508],
            # },

    # {
    #     "name": "MENTION",
    #     "type": "bar",
    #     "stack": "total",
    #     "label": {"show": True},
    #     "emphasis": {"focus": "series"},
    #     # "itemStyle": {"color": "#0000ff"},
    #     "data": [100, 302, 301, 334, 390, 330, 320, 301, 334, 390, 88, 99],
    # },


    # series = [
    #         {
    #             "name": "MENTION",
    #             "type": "bar",
    #             "stack": "total",
    #             "label": {"show": True},
    #             "emphasis": {"focus": "series"},
    #             # "itemStyle": {"color": "#0000ff"},
    #             "data": [100, 302, 301, 334, 390, 330, 320, 301, 334, 390, 88, 99],
    #         },
    #         {
    #             "name": "BAD",
    #             "type": "bar",
    #             "stack": "total",
    #             "label": {"show": True},
    #             "emphasis": {"focus": "series"},
    #             "data": [555, 132, 101, 134, 90, 230, 210, 101, 134, 90, 230, 99],
    #         },
    #         {
    #             "name": "GOOD",
    #             "type": "bar",
    #             "stack": "total",
    #             "label": {"show": True},
    #             "emphasis": {"focus": "series"},
    #             "data": [100, 182, 191, 234, 290, 330, 310, 191, 234, 290, 330, 310],
    #         },
    #         {
    #             "name": "MUSIC",
    #             "type": "bar",
    #             "stack": "total",
    #             "label": {"show": True},
    #             "emphasis": {"focus": "series"},
    #             "data": [150, 212, 201, 154, 190, 330, 410, 201, 154, 190, 330, 410],
    #         },
    #         {
    #             "name": "ENT",
    #             "type": "bar",
    #             "stack": "total",
    #             "label": {"show": True},
    #             "emphasis": {"focus": "series"},
    #             "data": [820, 832, 901, 934, 1290, 1330, 1320, 901, 934, 1290, 1330, 1320],
    #         },

    #         {
    #             "name": "CONTRACT",
    #             "type": "bar",
    #             "stack": "total",
    #             "label": {"show": True},
    #             "emphasis": {"focus": "series"},
    #             "data": [820, 832, 901, 934, 1290, 1330, 1320, 901, 934, 1290, 1330, 1320],
    #         },
    #         {
    #             "name": "AD",
    #             "type": "bar",
    #             "stack": "total",
    #             "label": {"show": True},
    #             "emphasis": {"focus": "series"},
    #             "data": [120, 132, 101, 134, 90, 230, 210, 101, 134, 90, 230, 99],
    #         },

    #         {
    #             "name": "RIP",
    #             "type": "bar",
    #             "stack": "total",
    #             "label": {"show": True},
    #             "emphasis": {"focus": "series"},
    #             "data": [120, 132, 101, 134, 90, 230, 210, 101, 134, 90, 230, 99],
    #         },
    #         {
    #             "name": "NO",
    #             "type": "bar",
    #             "stack": "total",
    #             "label": {"show": True},
    #             "emphasis": {"focus": "series"},
    #             "data": [120, 132, 101, 134, 90, 230, 210, 101, 134, 90, 230, 99],
    #         },
    #     ]


