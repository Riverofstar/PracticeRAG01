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

# 초기 상태 설정
def init_session_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "processComplete" not in st.session_state:
        st.session_state.processComplete = None
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [{"role": "assistant", 
                                         "content": "안녕하세요! 주어진 문서에 대해 궁금하신 것이 있으면 언제든 물어봐주세요!"}]

# 벡터스토어 생성
def get_vectorstore(text_chunks):
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

# 보드게임 추천 함수
def show_recommended_games(genre):
    filtered_games = df_games[df_games['장르'].str.contains(genre, na=False)]['게임 이름'].tolist()
    random.shuffle(filtered_games)
    return filtered_games[:5]

# 보드게임 설명 함수
def get_game_details(game_name):
    game_row = df_gameinfo[df_gameinfo['보드게임이름'].str.lower() == game_name.lower()]
    if not game_row.empty:
        details = game_row.iloc[0]
        # 줄바꿈 문자를 <br>로 대체
        game_rules = details['게임규칙'].replace('\n', '<br>')
        response = (
            f"<strong>보드게임 이름:</strong> {details['보드게임이름']}<br>"
            f"<strong>장르:</strong> {details['보드게임장르']}<br>"
            f"<strong>간략 소개:</strong> {details['보드게임간략소개']}<br>"
            f"<strong>플레이 인원수:</strong> {details['보드게임플레이인원수']}<br>"
            f"<strong>게임 규칙</strong><br> {game_rules}"  # 게임 규칙 텍스트 후 줄바꿈 추가
        )
        return response
    else:
        return "해당 보드게임에 대한 정보를 찾을 수 없습니다."



# 보드게임 추천 처리 함수
def handle_game_recommendation_from_csv(query):
    # 지원하는 장르 목록
    genres = ['마피아', '순발력', '파티', '전략', '추리', '협력', '액션']
    
    # 사용자가 언급한 장르 찾기
    found_genre = None
    for genre in genres:
        if genre in query:
            found_genre = genre
            break

    if found_genre:
        # 해당 장르의 보드게임 필터링
        filtered_games = df_gameinfo[df_gameinfo['보드게임장르'].str.contains(found_genre, na=False)]['보드게임이름'].tolist()
        if filtered_games:
            recommended_games = random.sample(filtered_games, min(5, len(filtered_games)))
            recommendation_response = [f"{found_genre} 장르의 추천 보드게임 목록은 다음과 같습니다:"]
            recommendation_response.extend([f"◾ {game}" for game in recommended_games])
        else:
            recommendation_response = [f"죄송합니다. {found_genre} 장르의 보드게임 정보를 찾을 수 없습니다."]
    else:
        recommendation_response = ["질문에 언급된 장르가 없습니다. 예를 들어 '추리 장르 보드게임 추천해줘'와 같은 질문을 해보세요."]

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
            genre = st.selectbox("장르 선택", ['마피아', '순발력', '파티', '전략', '추리', '협력'])
            if genre:
                st.write("다음 보드게임들을 추천합니다:")
                recommended_games = show_recommended_games(genre)
                st.write("\n".join(recommended_games))

        elif st.session_state.service == 'cafe_recommendation':
            st.markdown("<h3 style='font-size: 20px;'>어디에서 하실 예정인가요?</h3>", unsafe_allow_html=True)
            location = st.selectbox("지역 선택", ['홍대', '신촌', '건대입구', '이수', '강남역', '부천'])
            if location:
                st.write("다음 카페들을 추천합니다:")
                cafes = show_recommended_cafes(location)
                for cafe in cafes:
                    cafe_data = df_cafes[df_cafes['카페 이름'] == cafe].iloc[0]
                    review_count = cafe_data['방문자리뷰수']
                    naver_map_url = cafe_data['네이버지도주소']
                    st.write(f"- {cafe} (방문자리뷰: {review_count}) ")
                    st.markdown(f"[➡️ 네이버 지도]({naver_map_url})", unsafe_allow_html=True)

        elif st.session_state.service == 'chat_with_fairy':
            st.markdown("<h3 style='font-size: 20px;'>보드게임 요정에게 질문하기</h3>", unsafe_allow_html=True)

            if st.session_state.conversation is None:
                text_chunks = df_gameinfo['보드게임간략소개'].tolist() + df_cafeinfo['카페간략소개'].tolist()
                vetorestore = get_vectorstore(text_chunks)
                st.session_state.conversation = get_conversation_chain(vetorestore, os.getenv("OPENAI_API_KEY"))

            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.markdown(msg["content"])
                elif msg["role"] == "assistant":
                    with st.chat_message("assistant"):
                        st.markdown(msg["content"])

            if query := st.chat_input("질문을 입력해주세요."):
                st.session_state.messages.append({"role": "user", "content": query})
                with st.chat_message("user"):
                    st.markdown(query)

                found_game = None
                for game in df_gameinfo['보드게임이름'].tolist():
                    if game.lower() in query.lower():
                        found_game = game
                        break

                if found_game:
                    response = get_game_details(found_game)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.markdown(response, unsafe_allow_html=True)
                else:
                    with st.chat_message("assistant"):
                        if "보드게임" in query and "추천" in query and "보드게임 카페" not in query:
                            recommendation_response = handle_game_recommendation_from_csv(query)
                            for line in recommendation_response:
                                st.session_state.messages.append({"role": "assistant", "content": line})
                                st.markdown(line)
                        else:
                            chain = st.session_state.conversation
                            with st.spinner("Thinking..."):
                                result = chain({"question": query})
                                st.session_state.chat_history = result['chat_history']
                                chat_response = result['answer']
                                st.session_state.messages.append({"role": "assistant", "content": chat_response})
                                st.markdown(chat_response)

if __name__ == "__main__":
    main()
