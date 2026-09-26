                with st.container(key=f"ai_answer_{scope}_{item['id']}"):
                    answer = item["answer"]
                    label = {"searched": "논문·학술자료 검색 답변", "education": "교육자료 기반 답변",
                             "urgent": "우선 확인할 안내", "error": "연결 안내"}.get(answer["status"], "AI 답변")
                    st.markdown(f'<div class="answer-badge">{label}</div>', unsafe_allow_html=True)
                    if answer.get("notice"):
                        st.caption(answer["notice"])
                    st.markdown(answer["text"])
                    if answer.get("sources"):
                        st.caption("참고한 출처 · 제목을 누르면 원문 페이지로 이동합니다.")
                        for source in answer["sources"]:
                            title = re.sub(r"([\\`*_{}\[\]<>])", r"\\\1", source["title"])
                            st.markdown(f"[{source['number']}. {title}](<{source['url']}>)")
                    st.markdown(
                        "<div class='free-answer-note'><b>주의사항</b>: "
                        "AI 답변은 참고용이며, 진단·치료 결정은 담당 의료진과 상담하세요.</div>",
                        unsafe_allow_html=True,
                    )
            elif (
                st.session_state.pending_scope == scope
                and st.session_state.pending_qa_id == item["id"]
            ):
                st.caption("챗봇이 응답 중입니다…")


def render_free_questions(scope):
    with st.container(key=f"free_panel_{scope}"):
        render_free_questions_content(scope)


def render_free_questions_content(scope):
    render_free_question_title()
    st.html('<p class="question-privacy">질문은 외부 AI로 전송됩니다. 개인정보를 입력하지 마세요.</p>')
    pending = st.session_state.pending_scope == scope and bool(st.session_state.pending_prompt)
    # Nesting the input keeps it directly below the education text, not pinned to the browser.
    with st.container(key=f"question_input_{scope}"):
        user = st.chat_input(
            "챗봇이 응답 중입니다…" if pending else "궁금한 내용을 입력하세요.",
            key=f"chat_input_{scope}_{st.session_state.input_epoch}",
            max_chars=2000,
            disabled=pending,
        )
    with st.expander("AI 답변 이용 안내", expanded=False):
        for notice in education.FREE_QUESTION_NOTICES:
            st.caption(notice)
    if user and user.strip():
        add_pending_free_question(scope, user.strip())
        st.rerun()
    if pending:
        prompt = st.session_state.pending_prompt
        qa_id = st.session_state.pending_qa_id
        with st.spinner("질문에 맞는 근거를 확인하고 있습니다…"):
            answer = generate_answer(prompt, scope)
        save_free_question_answer(scope, qa_id, answer)
        st.session_state.pending_prompt = None
        st.session_state.pending_scope = None
        st.session_state.pending_qa_id = None
        st.rerun()
    render_free_qa_history(scope)


def render_navigation():
    if st.session_state.view == "home":
        return
    with st.container(key="page_navigation"):
        home_col, back_col = st.columns(2, gap="small")
        with home_col:
            st.button("🏠 첫 화면", key="nav_home", on_click=go_home, use_container_width=True)
        with back_col:
            st.button("이전", key="nav_back", on_click=go_back, use_container_width=True)


def render_education_item(item):
    with st.container(key=f"education_content_{item['id']}"):
        paragraphs = "".join(f"<p>{escape(text)}</p>" for text in item["paragraphs"])
        st.markdown(f'<div class="education-answer">{paragraphs}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="education-source">출처: {escape(item["source"])}</div>',
                    unsafe_allow_html=True)
        for reference in item["references"]:
            st.caption(reference)
    render_free_questions(f"answer_{item['id']}")


render_top_helper_bar("header")
render_navigation()

if st.session_state.view == "home":
    for start in range(0, len(MODULE_ORDER), 2):
        columns = st.columns(2)
        for column, mid in zip(columns, MODULE_ORDER[start:start + 2]):
            module = MODULES[mid]
            with column:
                st.button(f"{module['icon']} {mid}. {module['name']}",
                          key=f"home_module_{mid}", on_click=select_module, args=(mid,),
                          use_container_width=True)
    # Keep the first-screen chatbot underneath all eight topics.
    render_free_questions("home")

elif st.session_state.view == "topics":
    mid = st.session_state.module
    module = MODULES[mid]
    st.markdown(f'<div class="module-title">{escape(module["icon"])} {mid}. '
                f'{escape(module["name"])}</div>', unsafe_allow_html=True)
    for item in module["items"]:
        opened = st.session_state.question == item["id"]
        st.button(f"{item['id']} {item['title']}", key=f"question_{item['id']}",
                  on_click=select_question, args=(mid, item["id"]), use_container_width=True,
                  type="primary" if opened else "secondary",
                  help="이 내용을 접기" if opened else "이 내용 펼치기")
        if opened:
            render_education_item(item)

elif st.session_state.view == "free":
    render_free_questions("free_page")

# No hospital name, booking number, hospital branding or claim of institutional approval.
st.caption(education.COMMON_GUIDANCE[0])
with st.expander("📚 교육내용 근거"):
    for source in education.GUIDELINE_SOURCES:
        st.markdown(f"- {source}")
    st.caption("세부 복약·식사·기기·맥박 측정의 보충 근거는 각 교육항목의 출처를 확인하세요.")
