import streamlit as st
import openai
import os
import pandas as pd
import random
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI

# API 키 설정
os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]

# 추천용 데이터 불러오기
df_games = pd.read_csv('boardgames.csv')
df_cafes = pd.read_csv('cafes.csv')

# RAG 챗봇용 데이터 불러오기
df_gameinfo = pd.read_csv('gameinfo.csv')
df_cafeinfo = pd.read_csv('cafeinfo.csv')

# '보드게임이름' 및 '보드게임장르' 열의 공백 제거 버전을 추가
df_gameinfo['보드게임이름_no_space'] = df_gameinfo['보드게임이름'].str.replace(" ", "").str.lower()
df_gameinfo['보드게임장르_no_space'] = df_gameinfo['보드게임장르'].str.replace(" ", "").str.lower()

# 초기 상태 설정
def init_session_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "processComplete" not in st.session_state:
        st.session_state.processComplete = None
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [{
            "role": "assistant", 
            "content": "안녕하세요! 보드게임 요정입니다. 다음과 같은 질문이 가능합니다.<br>"
                       "-보드게임 추천<br>"
                       "-보드게임에 대한 정보 질문<br>"
                       "-장르기반 게임추천"
        }]

# 벡터스토어 생성
def get_vectorstore(dataframes):
    text_chunks = []
    
    for df in dataframes:
        # 각 데이터프레임의 모든 행을 문자열로 결합하여 하나의 텍스트로 만듦
        for _, row in df.iterrows():
            text_chunk = " ".join([str(value) for value in row.values if pd.notnull(value)])
            text_chunks.append(text_chunk)

    documents = [Document(page_content=chunk) for chunk in text_chunks]
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vectordb = FAISS.from_documents(documents, embeddings)
    return vectordb

# 대화 체인 생성
def get_conversation_chain(vetorestore, openai_api_key):
    llm = ChatOpenAI(openai_api_key=openai_api_key, model_name='gpt-3.5-turbo', temperature=0)

    if "chat_memory" not in st.session_state:
        st.session_state.chat_memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True,
            output_key='answer'
        )

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        chain_type="stuff",
        retriever=vetorestore.as_retriever(search_type='similarity', verbose=True),
        memory=st.session_state.chat_memory,
        get_chat_history=lambda h: h,
        return_source_documents=True,
        verbose=True
    )
    return conversation_chain

# 보드게임 설명 함수
def get_game_details(game_name):
    game_name_no_space = game_name.replace(" ", "").lower()
    game_row = df_gameinfo[df_gameinfo['보드게임이름_no_space'] == game_name_no_space]

    if not game_row.empty:
        details = game_row.iloc[0]
        game_rules = details['게임규칙'].replace('\n', '<br>')
        response = (
            f"<strong>보드게임 이름:</strong> {details['보드게임이름']}<br>"
            f"<strong>장르:</strong> {details['보드게임장르']}<br>"
            f"<strong>간략 소개:</strong> {details['보드게임간략소개']}<br>"
            f"<strong>플레이 인원수:</strong> {details['보드게임플레이인원수']}<br>"
            f"<strong>게임 규칙</strong><br> {game_rules}"
        )
        return response
    else:
        return "해당 보드게임에 대한 정보를 찾을 수 없습니다."

# 보드게임 추천 처리 함수
def handle_game_recommendation_from_csv(query):
    # 확장된 장르 목록
    genres = ['전략', '추리', '카드', '주사위', '파티', '블러핑', '협력', '퍼즐', '탐험', '모험', '순발력', 
              '경제', '덱 빌딩', '협상', '대결', '수확', '듀얼', '여행', '점수', '추상', '단어', '트릭 테이킹', 
              '경영', '기억', '레이싱', '팀', '경로 설정', '어드벤처', '공포', '실시간', '엔진 빌딩', '농장 경영', 
              '패스', '점령', '거래', '퀴즈', '숫자 조합', '숫자', '자원 관리', '숫자 맞추기', '탐정', '카드 거래', 
              '스피드', '정치', '순위']

    query_no_space = query.replace(" ", "").lower()

    # '게임'과 '추천' 키워드가 포함된 경우에만 추천 동작
    if "게임" in query_no_space and ("추천" in query_no_space or "좋을까" in query_no_space or "알려줘" in query_no_space):
        found_genre = None

        # '장르'라는 단어가 들어갈 경우 장르 필터링
        for genre in genres:
            genre_no_space = genre.replace(" ", "").lower()
            if genre_no_space in query_no_space:
                found_genre = genre
                break

        if found_genre:
            # 특정 장르의 보드게임 필터링
            filtered_games = df_gameinfo[df_gameinfo['보드게임장르_no_space'].str.contains(found_genre.replace(" ", "").lower(), na=False)]['보드게임이름'].tolist()
            
            if filtered_games:
                recommended_games = random.sample(filtered_games, min(5, len(filtered_games)))
                recommendation_response = [f"{found_genre} 장르의 추천 게임 목록은 다음과 같습니다:"]
                recommendation_response.extend([f"◾ {game}" for game in recommended_games])
            else:
                # 특정 장르의 게임이 없는 경우 오류 메시지
                recommendation_response = [f"죄송합니다. '{found_genre}' 장르의 게임 정보를 찾을 수 없습니다."]
        else:
            # 장르가 언급되지 않은 경우 전체 보드게임 추천
            all_games = df_gameinfo['보드게임이름'].tolist()
            if all_games:
                recommended_games = random.sample(all_games, min(5, len(all_games)))
                recommendation_response = ["추천할 수 있는 보드게임 목록은 다음과 같습니다:<br>" + "<br>".join([f"◾ {game}" for game in recommended_games])]
            else:
                recommendation_response = ["현재 보드게임 데이터를 찾을 수 없습니다."]
    else:
        recommendation_response = ["질문을 이해하지 못했습니다. 다시 질문해 주세요."]

    return recommendation_response

# 메인 함수
def main():
    init_session_state()

    st.markdown("<h1 style='font-size: 24px;'>보드게임 추천 시스템</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size: 18px;'>원하시는 서비스를 선택하세요:</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🎲 보드게임 추천"):
            st.session_state.service = 'game_recommendation'
    with col2:
        if st.button("🏠 보드게임 카페 추천"):
            st.session_state.service = 'cafe_recommendation'
    with col3:
        if st.button("🧚 보드게임 요정에게 질문하기"):
            st.session_state.service = 'chat_with_fairy'

    if 'service' in st.session_state:
        if st.session_state.service == 'game_recommendation':
            st.markdown("<h3 style='font-size: 20px;'>어떠한 장르의 보드게임을 찾으시나요?</h3>", unsafe_allow_html=True)
            genre = st.selectbox("장르 선택", ['전략', '추리', '카드', '파티', '협력', '모험', '퍼즐', '공포', '기타'])
            
            if genre:
                st.write("추천 보드게임:")
                recommended_games = df_gameinfo[df_gameinfo['보드게임장르'].str.contains(genre, na=False)]['보드게임이름'].tolist()
                if recommended_games:
                    random.shuffle(recommended_games)
                    for game in recommended_games[:5]:
                        st.write(f"◾ {game}")
                else:
                    st.write(f"'{genre}' 장르의 보드게임을 찾을 수 없습니다.")

        elif st.session_state.service == 'chat_with_fairy':
            st.markdown("<h3 style='font-size: 20px;'>보드게임 요정에게 질문하기</h3>", unsafe_allow_html=True)

            if st.session_state.conversation is None:
                vetorestore = get_vectorstore([df_gameinfo, df_cafeinfo])
                st.session_state.conversation = get_conversation_chain(vetorestore, os.getenv("OPENAI_API_KEY"))

            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.markdown(msg["content"], unsafe_allow_html=True)
                elif msg["role"] == "assistant":
                    with st.chat_message("assistant"):
                        st.markdown(msg["content"], unsafe_allow_html=True)

            if query := st.chat_input("질문을 입력해주세요."):
                st.session_state.messages.append({"role": "user", "content": query})
                with st.chat_message("user"):
                    st.markdown(query, unsafe_allow_html=True)

                # '게임'과 '추천' 키워드가 포함된 경우 처리
                if "게임" in query and ("추천" in query or "좋을까" in query or "알려줘" in query):
                    response = handle_game_recommendation_from_csv(query)
                    for line in response:
                        st.session_state.messages.append({"role": "assistant", "content": line})
                        st.markdown(line, unsafe_allow_html=True)
                else:
                    # gameinfo.csv의 보드게임 이름을 기준으로 검색
                    found_game = None
                    for game_name in df_gameinfo['보드게임이름']:
                        if game_name.lower().replace(" ", "") in query.lower().replace(" ", ""):
                            found_game = game_name
                            break
                    
                    if found_game:
                        game_details = get_game_details(found_game)
                        st.session_state.messages.append({"role": "assistant", "content": game_details})
                        st.markdown(game_details, unsafe_allow_html=True)
                    else:
                        # 대화 체인 사용
                        with st.chat_message("assistant"):
                            chain = st.session_state.conversation
                            with st.spinner("Thinking..."):
                                result = chain({"question": query})
                                st.session_state.chat_history = result['chat_history']
                                chat_response = result['answer']
                                st.session_state.messages.append({"role": "assistant", "content": chat_response})
                                st.markdown(chat_response, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
