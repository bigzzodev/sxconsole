import os
import yaml
import requests
import pickle
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st
from analytics import ST_ANALYTICS
# from operator import itemgetter
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, load_prompt, MessagesPlaceholder
# from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableMap
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser, JsonOutputParser
from langchain_core.embeddings import Embeddings
from langchain_core.messages.chat import ChatMessage
# from langchain_core.documents import Document
# from langchain_core.example_selectors import MaxMarginalRelevanceExampleSelector, SemanticSimilarityExampleSelector
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.callbacks.manager import get_openai_callback
# 아래는 pydantic 보다 기능이 떨어지는 llm 에서 사용
# from langchain.output_parsers import ResponseSchema, StructuredOutputParser, OutputFixingParser
# from langchain.output_parsers.enum import EnumOutputParser
from langchain import hub
from pinecone.grpc import PineconeGRPC as Pinecone
# from pinecone_text.sparse import BM25Encoder
# from pinecone import ServerlessSpec
from src import KiwiBM25Tokenizer
from src import PineconeKiwiHybridRetriever
from src import rag_db_namespace
from common import env

ST_USER = "user"
ST_ASSISTANT = "assistant"
ST_PICKLE_DIR = 'pickle'
ST_QNA_TOPK = 30
ST_QNA_ALPHA = 0.5
#
ST_TRACE = 'console-test9'
RAG_DB_INDEX = 'bigzzodev-db-index'

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
def _prompt_template_yaml():
    # yamlfile = os.path.join(sx_root_dir, PROMPTS_DIR, f'{_name}{SX_EXT_YAML}')
    try:
        with open('./prompts/prompt_req.yaml', 'r') as file:
            content = yaml.safe_load(file)
        return content
    except Exception as err:
        # raise InternalLlmError(err)
        raise

# ---------------------------------------------------------------------------------------
# def fmt_docs(docs):
#     res_str = '\n'.join([f"<document>{doc.page_content}</document>" for doc in docs])
#     return f"<context>{res_str}</context>"
def fmt_docs(docs):
    return '\n'.join([doc.page_content for doc in docs])

# ---------------------------------------------------------------------------------------
def page_header():
    st.set_page_config(page_icon = ':sparkles:', page_title = 'TechLab', layout = 'wide',)
    # st.title('_:red[Musicow] :gray[Techlab]_ :goat:')
    # if not os.getenv("OPENAI_API_KEY"):
    #     st.info('Enter an OpenAI API Key to continue')
    #     st.stop()



# ---------------------------------------------------------------------------------------
def _add_message(role, content, messages_key):
    # st.session_state[messages_key].append({"role": role, "content": content})
    st.session_state[messages_key].append(ChatMessage(role=role, content=content))

# ---------------------------------------------------------------------------------------
def _print_message(messages_key):
    for chat_message in st.session_state[messages_key]:
        # with st.chat_message(message["role"]):
        #     st.write(message["content"])
        st.chat_message(chat_message.role).write(chat_message.content)

# # ---------------------------------------------------------------------------------------
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
#     llm = ChatOpenAI(model_name='gpt-4o', temperature=0)
#     output_parser = StrOutputParser()
#     chain = prompt | llm | output_parser
#     return chain

# # ---------------------------------------------------------------------------------------
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
def qna_main(_selected, _user_input):
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
            top_k=ST_QNA_TOPK,
            alpha=ST_QNA_ALPHA,  # 0:키워드매칭
        )
        retriever = PineconeKiwiHybridRetriever(**pparams)
        search_res = retriever.invoke(_user_input, search_kwargs={'alpha': ST_QNA_ALPHA, 'k': ST_QNA_TOPK})
        for rx in search_res:
            print('\n---------------------------------------------------------------')
            print(f'>> {rx.metadata['classname']}')
            print(f'>> {rx.metadata['date']}\n')
            print(rx.page_content)
            print('\n')
        px = _prompt_template_yaml()
        prompt = PromptTemplate.from_template(px['prompt'])
        prompt = prompt.partial(singer=_selected)

        GPT_4o_mini = 'gpt-4o-mini-2024-07-18'
        llm = ChatOpenAI(model_name=GPT_4o_mini, openai_api_key=env.openai_api_key, temperature=0.0, verbose=True)
        chain = (
            {'context': retriever | fmt_docs, 'question': RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        response = chain.invoke(_user_input)
        if response is None:
            response = "답변을 생성할 수 없습니다."
        print(response)
        return response

    except Exception as e:
        # logger.error(f'[*] ssak3-index encountered an error : {e}')
        print(f'>> error : {e}')

# # ---------------------------------------------------------------------------------------
# def display_main(_selected, clear_btn):
#     def _handle_user_interaction():
#         st.session_state["waiting_for_answer"] = True

#     if 'messages' not in st.session_state:
#         st.session_state['messages'] = []
#         _add_message(ST_ASSISTANT, f'무엇이 궁금하세요?')

#     if "waiting_for_answer" not in st.session_state:
#         st.session_state["waiting_for_answer"] = False

#     if clear_btn:
#         st.session_state['messages'] = []
#         _add_message(ST_ASSISTANT, '무엇이 궁금하세요?')
#     _print_message()

#     # user_input = st.chat_input('say something')
#     if user_input := st.chat_input("Ask a question", on_submit=_handle_user_interaction, disabled=st.session_state["waiting_for_answer"]):
#         with st.chat_message(ST_USER):
#             st.write(user_input)
#         _add_message(ST_USER, user_input)
#         with st.chat_message(ST_ASSISTANT):
#             with st.spinner('Loading...'):
#                 response = qna_main(_selected, user_input)  # 응답을 기다리는 동안 스피너 표시
#                 st.write(response)  # 응답이 완료되면 표시
#         _add_message(ST_ASSISTANT, response)

#     if st.session_state["waiting_for_answer"]:
#         st.session_state["waiting_for_answer"] = False
#         st.rerun()

# ---------------------------------------------------------------------------------------
def display_main(_selected, clear_btn):
    messages_key = f"messages_{_selected}"
    waiting_for_answer_key = f"waiting_for_answer_{_selected}"

    def _handle_user_interaction():
        st.session_state[waiting_for_answer_key] = True

    if messages_key not in st.session_state:
        st.session_state[messages_key] = []
        _add_message(ST_ASSISTANT, f'무엇이 궁금하세요?', messages_key)

    if waiting_for_answer_key not in st.session_state:
        st.session_state[waiting_for_answer_key] = False

    if clear_btn:
        st.session_state[messages_key] = []
        _add_message(ST_ASSISTANT, '무엇이 궁금하세요?', messages_key)
    _print_message(messages_key)

    if user_input := st.chat_input("Ask a question", on_submit=_handle_user_interaction, disabled=st.session_state[waiting_for_answer_key]):
        with st.chat_message(ST_USER):
            st.write(user_input)
        _add_message(ST_USER, user_input, messages_key)
        with st.chat_message(ST_ASSISTANT):
            with st.spinner('Loading...'):
                response = qna_main(_selected, user_input)  # 응답을 기다리는 동안 스피너 표시
                st.write(response)  # 응답이 완료되면 표시
        _add_message(ST_ASSISTANT, response, messages_key)

    if st.session_state[waiting_for_answer_key]:
        st.session_state[waiting_for_answer_key] = False
        st.rerun()

# ---------------------------------------------------------------------------------------
def display():

    def _store_value():
        st.session_state["xselected"] = st.session_state["_xselected"]

    # 임시 키에 값 로드 함수
    def _load_value():
        if "xselected" in st.session_state:
            st.session_state["_xselected"] = st.session_state["xselected"]


    with st.sidebar:
        st.subheader("뉴스기사 :red[질의 응답]")
        singer_opt = list(ST_ANALYTICS.keys())
        _load_value()
        selected = st.selectbox(label="질문할 가수를 선택하세요", options=singer_opt, key="_xselected", on_change=_store_value)

        # func, year_opt = ST_ANALYTICS[selected]
        # selected_year = st.selectbox(label="확인할 년도를 선택하세요", options=year_opt,)
        # st.write("You selected:", selected_year)

    with st.sidebar:
        clear_btn = st.button('대화 초기화')
        # option = st.selectbox('프롬프트를 선택해 주세요', ('기본모드', 'SNS 게시글', '요약'), index=0)

    st.subheader(f'"{selected}" 에 대해 질문하기')
    st.divider()
    display_main(selected, clear_btn)

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
