import streamlit as st
import os
import pandas as pd
import random

# API 키 설정
os.environ["OPENAI_API_KEY"] = st.secrets["openai"]["api_key"]

# 추천용 데이터 불러오기
df_games = pd.read_csv('boardgames.csv')
df_cafes = pd.read_csv('cafes.csv')

# RAG 챗봇용 데이터 불러오기
df_gameinfo = pd.read_csv('gameinfo.csv')
# df_cafeinfo = pd.read_csv('cafeinfo.csv')

def generate_game_info_template(game_data):
    # 템플릿에 맞춘 보드게임 정보 답변 생성
    return f"""
    [{game_data['보드게임이름']}]

    장르 : {game_data['보드게임장르']}
    보드게임소개 : {game_data['보드게임간략소개']}
    보드게임플레이인원수 : {game_data['보드게임플레이인원수']}
    게임규칙 : {game_data['게임규칙']}
    """

def find_game_info(question):
    # 질문에 포함된 보드게임 이름으로 정보 검색
    game_data = df_gameinfo[df_gameinfo['보드게임이름'].str.contains(question, case=False, na=False)]
    if not game_data.empty:
        return generate_game_info_template(game_data.iloc[0])
    return "해당 보드게임 정보가 없습니다."

def show_recommended_games(genre):
    # 장르에 맞는 보드게임 추천
    filtered_games = df_games[df_games['장르'].str.contains(genre, na=False)]['게임 이름'].tolist()
    random.shuffle(filtered_games)
    return filtered_games[:5]

def show_recommended_cafes(location):
    # 지역에 맞는 카페 추천
    filtered_cafes = df_cafes[df_cafes['지역'].str.contains(location, na=False)]['카페 이름'].tolist()
    random.shuffle(filtered_cafes)
    return filtered_cafes[:5]

def main():
    st.title("보드게임 추천 시스템")

    st.subheader("원하시는 서비스를 선택하세요:")
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
            st.subheader("어떠한 장르의 보드게임을 찾으시나요?")
            genre = st.selectbox("장르 선택", ['마피아', '순발력', '파티', '전략', '추리', '협력'])
            if genre:
                st.write("다음 보드게임들을 추천합니다:")
                games = show_recommended_games(genre)
                for game in games:
                    st.write(f"- {game}")

        elif st.session_state.service == 'cafe_recommendation':
            st.subheader("어디에서 하실 예정인가요?")
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
            st.subheader("보드게임 요정에게 질문하기")
            question = st.text_input("질문을 입력하세요:")
            if st.button("질문하기"):
                # 보드게임 정보 검색
                game_info = find_game_info(question)
                
                # 결과 출력
                st.write("요정:", game_info)

if __name__ == "__main__":
    main()


