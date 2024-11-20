import os
import yaml
import json
import requests
import pickle
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st
from analytics import ST_ANALYTICS
from datetime import datetime
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_core.example_selectors import MaxMarginalRelevanceExampleSelector, SemanticSimilarityExampleSelector
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, load_prompt, MessagesPlaceholder
# from langchain_core.prompts.few_shot import FewShotPromptTemplate
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser, JsonOutputParser
from langchain_community.callbacks.manager import get_openai_callback
# 아래는 pydantic 보다 기능이 떨어지는 llm 에서 사용
# from langchain.output_parsers import ResponseSchema, StructuredOutputParser, OutputFixingParser
# from langchain.output_parsers.enum import EnumOutputParser
from langchain_core.embeddings import Embeddings
# from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, load_prompt, MessagesPlaceholder
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from pinecone import ServerlessSpec
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone_text.sparse import BM25Encoder
from langchain import hub
from langchain_core.messages.chat import ChatMessage
from src import KiwiBM25Tokenizer
from src import PineconeKiwiHybridRetriever
from src import rag_db_namespace
from annotated_text import annotated_text, annotation, parameters
from common import env

from reports.stock_info import Stock
from reports.search import stock_search
from reports.comment import create_connection, create_table, insert_comment, get_all_comments

@st.cache_data
def cache_AI_report(ticker):
    return AI_report(ticker)

ST_TRACE = 'console-test9'

env.int_env()

def AI_report(_ticker):
    """
    분석에 필요한 정보를 제공해드립니다.
    세 개의 따옴표가 포함된 마크다운 보고서가 제공됩니다.
    재무 분석가로서 보고서에 담긴 수치를 자세히 살펴보고
    회사의 성장 추세와 재무 안정성을 평가하여 사용자들이 자유롭게 토론할 수 있도록 돕습니다.
    사람들이 공개 토론을 할 수 있도록 귀하의 의견을 제공하십시오.
    보고서를 한국어로 제출해주세요.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        I want you to act as a Financial Analyst.
        Want assistance provided by qualified individuals enabled with experience on understanding charts using technical analysis tools while interpreting macroeconomic environment prevailing across world consequently assisting customers acquire long term advantages requires clear verdicts therefore seeking same through informed predictions written down precisely! First statement contains following content- “Can you tell us what future stock market looks like based upon current conditions ?”.
        """),
        ("user", ''' 
        We provide the information necessary for analysis.
        Given markdown reports with triple quotes. 
        As a Financial Analyst, Take a closer look at the numbers in the report and evaluate the company's growth trends and financial stability to help users discuss freely.
        Provide your opinion to people so they can have an open discussion.
        Please provide the report in Korean.

        """
        {markdown}
        """
        ''')
    ])
    output_parser = StrOutputParser()

    GPT_4o_mini = 'gpt-4o-mini-2024-07-18'
    llm = ChatOpenAI(model_name=GPT_4o_mini, openai_api_key=env.openai_api_key, temperature=0.0, verbose=True)

    chain = prompt | llm | output_parser
    return chain.invoke({
        "markdown": Stock(_ticker).report_support()
    })

# # -----------------------------------------------------------------------------------------------------------------
# def _init_pinecone(
#     index_name: str,
#     namespace: str,
#     api_key: str,
#     sparse_encoder_path: str=None,
#     stwords: List[str]=None,
#     tokenizer: str="kiwi",
#     embeddings: Embeddings=None,
#     top_k: int=10,
#     alpha: float=0.5,
# ) -> Dict:
#     pc = Pinecone(api_key=api_key)
#     pcindex = pc.Index(index_name)
#     # {'dimension': 1536,
#     # 'index_fullness': 0.0,
#     # 'namespaces': {'test01': {'vector_count': 43},
#     #                 'test02': {'vector_count': 66},
#     #                 'test03': {'vector_count': 757},
#     #                 'test10': {'vector_count': 243}},
#     # 'total_vector_count': 1109}
#     # print(f"[init_pinecone_index]\n{pcindex.describe_index_stats()}")
#     try:
#         with open(sparse_encoder_path, "rb") as f:
#             bm25 = pickle.load(f)
#         if tokenizer == "kiwi":
#             bm25._tokenizer = KiwiBM25Tokenizer(stop_words=stwords)
#     except Exception as e:
#         print(f'>> error : {e}')
#         return {}

#     namespace_keys = pcindex.describe_index_stats()["namespaces"].keys()
#     if namespace not in namespace_keys:
#         raise ValueError(f"`{namespace}` 를 `{list(namespace_keys)}` 에서 찾지 못했습니다.")

#     return {
#         "index": pcindex,
#         "namespace": namespace,
#         "sparse_encoder": bm25,
#         "embeddings": embeddings,
#         "top_k": top_k,
#         "alpha": alpha,
#         "pc": pc,
#     }

# # -----------------------------------------------------------------------------------------------------------------
# def _stopwords():
#     file_url = "https://raw.githubusercontent.com/teddylee777/langchain-teddynote/main/assets/korean_stopwords.txt"
#     response = requests.get(file_url)
#     response.raise_for_status()
#     stopwords_data = response.text
#     stopwords = stopwords_data.splitlines()
#     return [word.strip() for word in stopwords]

# # -----------------------------------------------------------------------------------------------------------------
# # def _prompt_template_yaml():
# #     # yamlfile = os.path.join(sx_root_dir, PROMPTS_DIR, f'{_name}{SX_EXT_YAML}')
# #     try:
# #         with open('./prompts/prompt_req.yaml', 'r') as file:
# #             content = yaml.safe_load(file)
# #         return content
# #     except Exception as err:
# #         # raise InternalLlmError(err)
# #         raise


# ---------------------------------------------------------------------------------------
class SearchResult:
    def __init__(self, item):
        self.item = item

    @property
    def symbol(self):
        return self.item['Symbol']
    
    @property
    def name(self):
        return self.item['Name']

    def __str__(self):
        return f"{self.symbol}: {self.name}"

# ---------------------------------------------------------------------------------------
def page_header():
    st.set_page_config(page_icon = ':sparkles:', page_title = 'TechLab', layout = 'wide',)
    # st.title('_:red[Musicow] :gray[Techlab]_ :goat:')

# # ---------------------------------------------------------------------------------------
# # def _create_chain(_prompt_type):
# #     prompt = ChatPromptTemplate.from_messages(
# #         [
# #             ('system', '당신은 친절한 AI 어시스턴트입니다. 다음의 질문에 간결하게 답변해 주세요'),
# #             ('user', '#Question:\n{question}'),
# #         ]
# #     )
# #     if _prompt_type == 'SNS 게시글':
# #         prompt = load_prompt('prompts/sns.yaml', encoding='utf-8')
# #     elif _prompt_type == '요약':
# #         prompt = hub.pull('teddynote/chain-of-density-map-korean')
# #     GPT_4o_mini = 'gpt-4o-mini-2024-07-18'
# #     llm = ChatOpenAI(model_name=GPT_4o_mini, openai_api_key=env.openai_api_key, temperature=0.0, verbose=True)

# #     output_parser = StrOutputParser()
# #     chain = prompt | llm | output_parser
# #     return chain

# # ---------------------------------------------------------------------------------------
# def search_main(_selected, _user_input):
#     try:
#         emb = OpenAIEmbeddings(model='text-embedding-3-small', openai_api_key=env.openai_api_key)  # 1536
#         pparams = _init_pinecone(
#             index_name=RAG_DB_INDEX,
#             namespace=rag_db_namespace(_selected),
#             api_key=env.pinecone_api_key,
#             sparse_encoder_path=f'{ST_PICKLE_DIR}/day_{_selected}_sparse_encoder.pkl',
#             stwords=_stopwords(),
#             tokenizer='kiwi',
#             embeddings=emb,
#             top_k=ST_SEARCH_TOPK,
#             alpha=ST_SEARCH_ALPHA,  # 0:키워드매칭
#         )
#         retriever = PineconeKiwiHybridRetriever(**pparams)
#         search_res = retriever.invoke(_user_input, search_kwargs={'alpha': ST_SEARCH_ALPHA, 'k': ST_SEARCH_TOPK})
#         filtered_res = [rx for rx in search_res if _user_input in rx.page_content]
#         if not len(filtered_res):
#             return None, None, None, None
#         results_text = ""
#         classnames = []
#         dates = []
#         page_contents = []
#         for rx in filtered_res:
#             results_text += f"클래스명: {rx.metadata['classname']}\n"
#             results_text += f"날짜: {rx.metadata['date']}\n\n"
#             results_text += f"{rx.page_content}\n"
#             results_text += '-' * 60 + '\n\n'
#             classnames.append(rx.metadata['classname'])
#             dates.append(rx.metadata['date'])
#             page_contents.append(rx.page_content)
#         return results_text, classnames, dates, page_contents
#     except Exception as e:
#         # logger.error(f'[*] ssak3-index encountered an error : {e}')
#         print(f'>> error : {e}')

# # ---------------------------------------------------------------------------------------
# def display_main(_selected):
#     searching_key = f"searching_{_selected}"
#     search_queries_key = f"search_queries_{_selected}"
#     ress_key = f"ress_{_selected}"

    # def _search():
    #     st.session_state[searching_key] = True
    #     st.rerun()

    # def _results():
    #     with st.spinner("검색 중입니다..."):
    #         results_text, cname, date, content = search_main(_selected, st.session_state[search_queries_key])
    #     print(results_text)
    #     st.session_state[ress_key] = {
    #         'results_text': results_text,
    #         'cname': cname,
    #         'date': date,
    #         'content': content
    #     }
    #     st.session_state[searching_key] = False
    #     st.rerun()

    # if searching_key not in st.session_state:
    #     st.session_state[searching_key] = False
    # if search_queries_key not in st.session_state:
    #     st.session_state[search_queries_key] = ''

    # st.text_input("검색할 키워드를 입력하세요.", value=st.session_state[search_queries_key], key=search_queries_key, disabled=st.session_state[searching_key])
    # if st.button("검색") and not st.session_state[searching_key]:
    #     _search()
    # if st.session_state[searching_key]:
    #     _results()


# ---------------------------------------------------------------------------------------
def display_main(_selected):

    # Create a text input for search
    # search_query = st.text_input("검색창")
    # hits = stock_search(search_query)['hits']
    # hits = 5
    # search_results = [SearchResult(hit) for hit in hits]

    # search_results = ['11',]

    # Create a select box for search results list

    # selected = st.selectbox("검색 결과 리스트", search_results)

    # Create tabs for different sections
    tabs = ["가수 기본 정보", "가수 체크사항", "AI 분석 보고서"]
    tab1, tab2, tab3 = st.tabs(tabs)


    # Content for "회사 기본 정보" tab
    with tab1:

        from PIL import Image # 위에서 선언 후 사용해야한다.

        img = Image.open(f'data/{_selected}.png')
            # 경로에 있는 이미지 파일을 통해 변수 저장
        st.image(img, width=500)
            # streamlit를 통해 이미지를 보여준다.
        st.write('')

        # stock = Stock(selected.symbol)
        stock = Stock('AAPL')
        # st.header(str(selected))
        # 거래량 시각화
        st.subheader(f'거래량')
        stock_data = stock.금융정보()
        st.line_chart(stock_data['history']['Volume'])

        st.header("재무제표")
        cols = st.columns(3)
        cols[0].subheader("매출액")
        cols[0].line_chart(stock_data['income_statement'].loc['Total Revenue'])
        cols[1].subheader("순이익")
        cols[1].line_chart(stock_data['income_statement'].loc['Net Income'])
        cols[2].subheader("영업이익")
        cols[2].line_chart(stock_data['income_statement'].loc['Operating Income'])

        cols = st.columns(3)
        cols[0].subheader("자산")
        cols[0].line_chart(stock_data['balance_sheet'].loc['Total Assets'])
        cols[1].subheader("부채")
        cols[1].line_chart(stock_data['balance_sheet'].loc['Total Liabilities Net Minority Interest'])
        cols[2].subheader("자본")
        cols[2].line_chart(stock_data['balance_sheet'].loc['Stockholders Equity'])

        cols = st.columns(4)
        cols[0].subheader("영업 현금흐름")
        cols[0].line_chart(stock_data['cash_flow'].loc['Operating Cash Flow'])
        cols[1].subheader("투자 현금흐름")
        cols[1].line_chart(stock_data['cash_flow'].loc['Investing Cash Flow'])
        cols[2].subheader("재무 현금흐름")
        cols[2].line_chart(stock_data['cash_flow'].loc['Financing Cash Flow'])
        cols[3].subheader("순 현금흐름")
        cols[3].line_chart(stock_data['cash_flow'].loc['Free Cash Flow'])

    # Content for "종목 토론실" tab
    with tab2:
        st.header("가수 체크사항")
        conn = create_connection()
        create_table(conn)

        for comment in get_all_comments(conn):
            comment_time, comment_text = comment
            st.write(f"{comment_time}: {comment_text}")

        # 앞에서부터 그리기 때문에 댓글 입력창이 위에 나옴
        new_comment = st.text_area("댓글을 입력하세요")
        if st.button("댓글 작성"):
            insert_comment(conn, f'{_selected} - {new_comment}')
            st.success("댓글이 작성되었습니다")
            st.rerun()

    # Content for "AI 분석 보고서" tab
    with tab3:
        st.header("AI 분석 보고서")
        if st.button("보고서 불러오기"):
            with st.spinner(text='In progress'):
                # data = cache_AI_report(selected.symbol)
                data = cache_AI_report('AAPL')
                st.success('Done')
            st.write(data)


# ---------------------------------------------------------------------------------------
def display():

    def _store_value():
        st.session_state["xselected"] = st.session_state["_xselected"]

    # 임시 키에 값 로드 함수
    def _load_value():
        if "xselected" in st.session_state:
            st.session_state["_xselected"] = st.session_state["xselected"]

    with st.sidebar:
        st.subheader("뉴스기사 :violet[보고서 생성]")
        # 가수별 선택 옵션
        singer_opt = list(ST_ANALYTICS.keys())
        _load_value()
        selected = st.selectbox(label="보고서 생성할 가수를 선택하세요", options=singer_opt, key="_xselected", on_change=_store_value)

    # with st.sidebar:
        # clear_btn = st.button('검색 기록 초기화')
        # option = st.selectbox('검색 모드를 선택해 주세요', ('기본모드', 'SNS 게시글', '요약'), index=0)

    st.subheader(f'"{selected}" 보고서 생성 - (예시)')
    st.divider()
    display_main(selected)

# ---------------------------------------------------------------------------------------
if __name__ == '__main__':
    page_header()

    hide_streamlit_style = """
        <style>
        [data-testid="stToolbar"] {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        </style>
        """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    display()
    env.langsmith(ST_TRACE)