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

DIMENSION = 1536
RAG_DB_INDEX = 'bigzzodev-db-index'
ST_PICKLE_DIR = 'pickle'
ST_TRACE = 'console-test9'

ST_SEARCH_TOPK = 30
ST_SEARCH_ALPHA = 0
env.int_env()

# -----------------------------------------------------------------------------------------------------------------
def _init_pinecone(
    index_name: str,
    namespace: str,
    api_key: str,
    sparse_encoder_path: str=None,
    stwords: List[str]=None,
    tokenizer: str="kiwi",
    embeddings: Embeddings=None,
    top_k: int=10,
    alpha: float=0.5,
) -> Dict:
    pc = Pinecone(api_key=api_key)
    pcindex = pc.Index(index_name)
    # {'dimension': 1536,
    # 'index_fullness': 0.0,
    # 'namespaces': {'test01': {'vector_count': 43},
    #                 'test02': {'vector_count': 66},
    #                 'test03': {'vector_count': 757},
    #                 'test10': {'vector_count': 243}},
    # 'total_vector_count': 1109}
    # print(f"[init_pinecone_index]\n{pcindex.describe_index_stats()}")
    try:
        with open(sparse_encoder_path, "rb") as f:
            bm25 = pickle.load(f)
        if tokenizer == "kiwi":
            bm25._tokenizer = KiwiBM25Tokenizer(stop_words=stwords)
    except Exception as e:
        print(f'>> error : {e}')
        return {}

    namespace_keys = pcindex.describe_index_stats()["namespaces"].keys()
    if namespace not in namespace_keys:
        raise ValueError(f"`{namespace}` 를 `{list(namespace_keys)}` 에서 찾지 못했습니다.")

    return {
        "index": pcindex,
        "namespace": namespace,
        "sparse_encoder": bm25,
        "embeddings": embeddings,
        "top_k": top_k,
        "alpha": alpha,
        "pc": pc,
    }

# -----------------------------------------------------------------------------------------------------------------
def _stopwords():
    file_url = "https://raw.githubusercontent.com/teddylee777/langchain-teddynote/main/assets/korean_stopwords.txt"
    response = requests.get(file_url)
    response.raise_for_status()
    stopwords_data = response.text
    stopwords = stopwords_data.splitlines()
    return [word.strip() for word in stopwords]

# -----------------------------------------------------------------------------------------------------------------
# def _prompt_template_yaml():
#     # yamlfile = os.path.join(sx_root_dir, PROMPTS_DIR, f'{_name}{SX_EXT_YAML}')
#     try:
#         with open('./prompts/prompt_req.yaml', 'r') as file:
#             content = yaml.safe_load(file)
#         return content
#     except Exception as err:
#         # raise InternalLlmError(err)
#         raise

# ---------------------------------------------------------------------------------------
def page_header():
    st.set_page_config(page_icon = ':sparkles:', page_title = 'TechLab', layout = 'wide',)
    # st.title('_:red[Musicow] :gray[Techlab]_ :goat:')
    st.divider()

# ---------------------------------------------------------------------------------------
# def _create_chain(_prompt_type):
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ('system', '당신은 친절한 AI 어시스턴트입니다. 다음의 질문에 간결하게 답변해 주세요'),
#             ('user', '#Question:\n{question}'),
#         ]
#     )
#     if _prompt_type == 'SNS 게시글':
#         prompt = load_prompt('prompts/sns.yaml', encoding='utf-8')
#     elif _prompt_type == '요약':
#         prompt = hub.pull('teddynote/chain-of-density-map-korean')
#     GPT_4o_mini = 'gpt-4o-mini-2024-07-18'
#     llm = ChatOpenAI(model_name=GPT_4o_mini, openai_api_key=env.openai_api_key, temperature=0.0, verbose=True)

#     output_parser = StrOutputParser()
#     chain = prompt | llm | output_parser
#     return chain

# ---------------------------------------------------------------------------------------
# def test01(_user_input):
#     chain = _create_chain('SNS 게시글')
#     # ----------------------------------------------------------------------------
#     # 한번에 출력
#     # ai_answer = chain.invoke({'question': user_input})
#     # st.chat_message('ai').write(ai_answer)         # 'assistant' 로 써도 동일함
#     # ----------------------------------------------------------------------------

#     # if option == '요약':
#     response = chain.stream({'question': _user_input})
#     # else:
#     #     response = chain.stream(user_input)

#     return response

# ---------------------------------------------------------------------------------------
def search_main(_selected, _user_input):
    try:
        emb = OpenAIEmbeddings(model='text-embedding-3-small', openai_api_key=env.openai_api_key)  # 1536
        pparams = _init_pinecone(
            index_name=RAG_DB_INDEX,
            namespace=rag_db_namespace(_selected),
            api_key=env.pinecone_api_key,
            sparse_encoder_path=f'{ST_PICKLE_DIR}/day_{_selected}_sparse_encoder.pkl',
            stwords=_stopwords(),
            tokenizer='kiwi',
            embeddings=emb,
            top_k=ST_SEARCH_TOPK,
            alpha=ST_SEARCH_ALPHA,  # 0:키워드매칭
        )
        retriever = PineconeKiwiHybridRetriever(**pparams)
        search_res = retriever.invoke(_user_input, search_kwargs={'alpha': ST_SEARCH_ALPHA, 'k': ST_SEARCH_TOPK})
        filtered_res = [rx for rx in search_res if _user_input in rx.page_content]
        if not len(filtered_res):
            return None, None, None, None
        results_text = ""
        classnames = []
        dates = []
        page_contents = []
        for rx in filtered_res:
            results_text += f"클래스명: {rx.metadata['classname']}\n"
            results_text += f"날짜: {rx.metadata['date']}\n\n"
            results_text += f"{rx.page_content}\n"
            results_text += '-' * 60 + '\n\n'
            classnames.append(rx.metadata['classname'])
            dates.append(rx.metadata['date'])
            page_contents.append(rx.page_content)
        return results_text, classnames, dates, page_contents
    except Exception as e:
        # logger.error(f'[*] ssak3-index encountered an error : {e}')
        print(f'>> error : {e}')

# ---------------------------------------------------------------------------------------
def display_main(_selected):
    searching_key = f"searching_{_selected}"
    search_queries_key = f"search_queries_{_selected}"
    ress_key = f"ress_{_selected}"

    def _search():
        st.session_state[searching_key] = True
        st.rerun()

    def _results():
        with st.spinner("검색 중입니다..."):
            results_text, cname, date, content = search_main(_selected, st.session_state[search_queries_key])
        print(results_text)
        st.session_state[ress_key] = {
            'results_text': results_text,
            'cname': cname,
            'date': date,
            'content': content
        }
        st.session_state[searching_key] = False
        st.rerun()

    if searching_key not in st.session_state:
        st.session_state[searching_key] = False
    if search_queries_key not in st.session_state:
        st.session_state[search_queries_key] = ''

    st.text_input("검색할 키워드를 입력하세요.", value=st.session_state[search_queries_key], key=search_queries_key, disabled=st.session_state[searching_key])
    if st.button("검색") and not st.session_state[searching_key]:
        _search()
    if st.session_state[searching_key]:
        _results()

    def _generate_annotated_text(_data):
        annotations = []
        for key, value in _data.items():
            annotations.append(annotation(key, f"({value})", font_family="Comic Sans MS", border="2px red"))
            annotations.append("  ")
        if annotations:
            annotations.pop()
        annotated_text(*annotations)

    if ress_key in st.session_state:
        if not st.session_state[ress_key]['content']:
            st.write('검색 결과가 없습니다.')
        else:
            combined_data = sorted(
                zip(st.session_state[ress_key]['date'], 
                    st.session_state[ress_key]['cname'], 
                    st.session_state[ress_key]['content']),
                key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"),
                reverse=True
            )
            for date_str, class_name, content_json_str in combined_data:
                content_json = json.loads(content_json_str)
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                st.subheader(date_obj.strftime("%Y년 %m월 %d일"))
                modified_text = class_name.replace("class_", "")
                st.info(f'**{modified_text}**')
                _generate_annotated_text(content_json['tags'])
                summary_list = content_json['summary']
                with st.expander("SUMMARY:"):
                    for _idx in summary_list:
                        st.code(_idx)

# ---------------------------------------------------------------------------------------
def display():

    def _store_value():
        st.session_state["xselected"] = st.session_state["_xselected"]

    # 임시 키에 값 로드 함수
    def _load_value():
        if "xselected" in st.session_state:
            st.session_state["_xselected"] = st.session_state["xselected"]

    with st.sidebar:
        st.subheader("뉴스기사 :blue[키워드 검색]")
        # 가수별 선택 옵션
        singer_opt = list(ST_ANALYTICS.keys())
        _load_value()
        selected = st.selectbox(label="검색할 가수를 선택하세요", options=singer_opt, key="_xselected", on_change=_store_value)

    # with st.sidebar:
        # clear_btn = st.button('검색 기록 초기화')
        # option = st.selectbox('검색 모드를 선택해 주세요', ('기본모드', 'SNS 게시글', '요약'), index=0)

    st.subheader(f'"{selected}" 키워드 검색')
    display_main(selected)

# ---------------------------------------------------------------------------------------
if __name__ == '__main__':
    page_header()
    display()
    env.langsmith(ST_TRACE)