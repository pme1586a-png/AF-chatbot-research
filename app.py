        [data-testid="stExpander"] {
            display:none !important;
            visibility:hidden !important;
            height:0 !important;
            min-height:0 !important;
            margin:0 !important;
            padding:0 !important;
            overflow:hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="answer-page-title">챗봇 답변</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="question-card">
            <div class="qa-label">질문</div>
            <div class="question-text">{html.escape(question)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.answer_text is None:
        # API 응답 동안 환자에게 명확한 대기 상태를 표시합니다.
        st.markdown(
            """
            <div class="answer-waiting">
                <div class="wait-anim-wrap">
                    <span class="wait-icon" aria-hidden="true">
                        <svg viewBox="0 0 32 32" fill="none">
                            <path d="M9 5h14M9 27h14" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
                            <path d="M11 6c0 5 2.8 7 5 9-2.2 2-5 4-5 11M21 6c0 5-2.8 7-5 9 2.2 2 5 4 5 11" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M13.2 10.2h5.6M13.1 22h5.8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                        </svg>
                    </span>
                    <span class="wait-dots"><span></span><span></span><span></span></span>
                </div>
                답변을 준비하고 있습니다.
                <span class="wait-sub">잠시만 기다려 주세요.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # 대기 중에도 이동 버튼을 화면에 보여줍니다.
        render_answer_nav()
        with st.spinner("응답 중입니다…"):
            st.session_state.answer_text = generate_answer(
                question,
                current_context=st.session_state.answer_context,
            )
        st.rerun()

    result = st.session_state.answer_text
    if isinstance(result, dict):
        answer_text = result.get("text", "")
        answer_sources = result.get("sources", []) or []
        answer_citations = result.get("citations", []) or []
        fallback_notice = result.get("fallback_notice")
    else:
        answer_text = str(result or "")
        answer_sources = []
        answer_citations = []
        fallback_notice = None

    # 실제 URL citation 위치에 구글 검색처럼 클릭 가능한 출처칩을 바로 붙입니다.
    marked_answer, inline_chip_sources = _apply_inline_source_placeholders(answer_text, answer_citations)
    cleaned_answer = _clean_answer_body(marked_answer)
    answer_html = _inline_text_to_html(cleaned_answer, inline_chip_sources)

    # citation 위치가 없는 예외적인 경우에만 카드 내부 맨 끝에 간단한 출처칩을 보조로 표시합니다.
    source_fallback_html = "" if inline_chip_sources else _fallback_source_chips_html(answer_sources)

    fallback_html = ""
    if fallback_notice:
        fallback_html = f'<div class="ai-fallback-notice">{html.escape(fallback_notice)}</div>'

    st.markdown(
        f"""
        <div class="answer-card">
            <div class="qa-label">AI 답변</div>
            <div class="answer-text">{answer_html}</div>
            {source_fallback_html}
            {fallback_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 답변 바로 아래에 이전 / 처음으로 버튼을 먼저 배치합니다.
    render_answer_nav()

    # 그 아래에서 바로 새 질문을 다시 입력할 수 있습니다.
    render_answer_followup()

    # 별도의 맨 아래 출처 목록은 표시하지 않습니다. 본문의 출처칩이 곧 링크입니다.


# 하단 고정 챗봇 질문 버튼은 제거함.


# =========================================================
# 교육내용 근거
# 병원명·병원 전화번호는 표시하지 않음.
# =========================================================
if st.session_state.view not in ("answer",):
    with st.expander("📚 교육내용 근거"):
        st.markdown(
            """
- 2024 대한부정맥학회 심방세동 일반 치료 진료지침
- 2024 대한부정맥학회 심방세동 시술적 치료 진료지침
- 2024 대한부정맥학회 심방세동 NOAC 치료 진료지침
- 2024 ESC Guidelines for the management of atrial fibrillation
            """
        )
