def main():
    init_session_state()

    # 제목과 서브헤더의 크기를 줄이기 위해 HTML과 CSS를 사용
    st.markdown("<h1 style='font-size: 32px;'>보드게임 추천 시스템</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size: 24px;'>원하시는 서비스를 선택하세요:</h2>", unsafe_allow_html=True)

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

    # 이하 코드 유지
    if 'service' in st.session_state:
        if st.session_state.service == 'game_recommendation':
            st.subheader("어떠한 장르의 보드게임을 찾으시나요?")
            genre = st.selectbox("장르 선택", ['마피아', '순발력', '파티', '전략', '추리', '협력'])
            if genre:
                st.write("다음 보드게임들을 추천합니다:")
                recommended_games = show_recommended_games(genre)
                st.write("\n".join(recommended_games))

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

            if st.session_state.conversation is None:
                text_chunks = df_gameinfo['보드게임간략소개'].tolist() + df_cafeinfo['카페간략소개'].tolist()
                vetorestore = get_vectorstore(text_chunks)
                st.session_state.conversation = get_conversation_chain(vetorestore, os.getenv("OPENAI_API_KEY"))

            if query := st.chat_input("질문을 입력해주세요."):
                st.session_state.messages.append({"role": "user", "content": query})
                with st.chat_message("user"):
                    st.markdown(query)

                with st.chat_message("assistant"):
                    if "보드게임" in query and "추천" in query and "보드게임 카페" not in query:
                        recommendation_response = handle_game_recommendation_from_csv(query)
                        st.markdown(recommendation_response)
                    else:
                        chain = st.session_state.conversation
                        with st.spinner("Thinking..."):
                            result = chain({"question": query})
                            st.session_state.chat_history = result['chat_history']
                            chat_response = result['answer']
                        st.markdown(chat_response)

if __name__ == "__main__":
    main()
