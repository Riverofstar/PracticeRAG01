#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import streamlit as st
import random
import pandas as pd

# 보드게임과 카페 데이터를 불러옵니다
df_games = pd.read_csv('boardgames.csv')
df_cafes = pd.read_csv('cafes.csv')

def show_recommended_games(genre):
    # 선택한 장르에 맞는 보드게임 필터링
    filtered_games = df_games[df_games['장르'] == genre]['name'].tolist()

    random.shuffle(filtered_games)  # 게임 목록을 랜덤으로 섞음
    return filtered_games[:5]  # 상위 5개의 게임만 반환

def show_recommended_cafes(location):
    # 선택한 지역에 맞는 카페 필터링
    filtered_cafes = df_cafes[df_cafes['지역'] == location]['name'].tolist()
    random.shuffle(filtered_cafes)  # 카페 목록을 랜덤으로 섞음
    return filtered_cafes[:5]  # 상위 5개의 카페만 반환

def main():
    st.title("보드게임 추천 시스템")

    # 첫 번째 선택지: 보드게임 추천과 보드게임 카페 추천
    st.subheader("원하시는 서비스를 선택하세요:")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎲 보드게임 추천"):
            st.session_state.service = 'game_recommendation'
    with col2:
        if st.button("🏠 보드게임 카페 추천"):
            st.session_state.service = 'cafe_recommendation'
    
    # 사용자가 선택한 서비스에 따라 다음 단계로 이동
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
                    st.write(f"- {cafe}")

if __name__ == "__main__":
    main()




