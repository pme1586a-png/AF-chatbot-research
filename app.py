                        unsafe_allow_html=True)
        with home_col:
            st.button("첫 화면", key="nav_home", on_click=go_home, use_container_width=True)


def render_bottom_navigation():
    with st.container(key="app_bottom_navigation"):
        education_col, chat_col = st.columns(2, gap="small")
        with education_col:
            st.button("교육 주제", key="tab_education", icon=":material/grid_view:",
                      type="primary" if st.session_state.view != "free" else "secondary",
                      on_click=go_home, use_container_width=True)
        with chat_col:
            st.button("챗봇 질문", key="tab_chat", icon=":material/chat_bubble_outline:",
                      type="primary" if st.session_state.view == "free" else "secondary",
                      on_click=go_free_question, use_container_width=True)


def render_education_item(item, position, total):
    with st.container(key=f"education_content_{item['id']}"):
        st.markdown(
            f'<div class="detail-position">{position:02d} / {total:02d}</div>'
            f'<h2 class="detail-title">{escape(item["title"])}</h2>',
            unsafe_allow_html=True,
        )
        paragraphs = "".join(f"<p>{escape(text)}</p>" for text in item["paragraphs"])
        st.markdown(f'<div class="education-answer">{paragraphs}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="education-source">출처: {escape(item["source"])}</div>',
                    unsafe_allow_html=True)
        for reference in item["references"]:
            st.caption(reference)


def render_detail_actions(mid, position):
    items = MODULES[mid]["items"]
    with st.container(key="detail_actions"):
        list_col, next_col = st.columns(2, gap="small")
        with list_col:
            st.button("하위주제 목록", key="detail_topic_list", on_click=go_back,
                      help="이 주제의 하위주제 목록으로 이동", use_container_width=True)
        with next_col:
            has_next = position < len(items)
            st.button("다음 내용 →" if has_next else "마지막 내용", key="detail_next",
                      on_click=next_education_item if has_next else None,
                      args=(mid, items[position]["id"]) if has_next else None,
                      disabled=not has_next, use_container_width=True)


render_top_helper_bar("header")
render_navigation()

if st.session_state.view == "home":
    st.markdown('<div class="section-heading"><h1>교육 주제</h1>'
                f'<span class="section-count">{len(MODULE_ORDER)}개 주제</span></div>',
                unsafe_allow_html=True)
    with st.container(key="home_topics"):
        for start in range(0, len(MODULE_ORDER), 2):
            columns = st.columns(2, gap="small")
            for column, mid in zip(columns, MODULE_ORDER[start:start + 2]):
                module = MODULES[mid]
                with column:
                    st.button(f"{mid}. {module['name']}",
                              key=f"home_module_{mid}", on_click=select_module, args=(mid,),
                              use_container_width=True)
    # Keep the first-screen chatbot underneath all eight topics.
    render_free_questions("home")

elif st.session_state.view == "topics":
    mid = st.session_state.module
    module = MODULES[mid]
    st.markdown(f'<div class="section-kicker">주제 {int(mid):02d}</div>'
                f'<h1 class="module-title">{escape(module["name"])}</h1>',
                unsafe_allow_html=True)
    st.caption(f'{len(module["items"])}개 하위주제 · 읽고 싶은 내용을 선택해 주세요.')
    with st.container(key="topic_list"):
        for position, item in enumerate(module["items"], 1):
            st.button(f"{position:02d} · {item['title']}", key=f"question_{item['id']}",
                      on_click=select_question, args=(mid, item["id"]),
                      use_container_width=True, help="내용 화면으로 이동")

elif st.session_state.view == "detail":
    mid = st.session_state.module
    module = MODULES[mid]
    st.markdown(f'<div class="module-context">{mid}. '
                f'{escape(module["name"])}</div>', unsafe_allow_html=True)
    for position, item in enumerate(module["items"], 1):
        if item["id"] == st.session_state.question:
            render_education_item(item, position, len(module["items"]))
            render_detail_actions(mid, position)
            render_free_questions(f"answer_{item['id']}")
            break

elif st.session_state.view == "free":
    render_free_questions("free_page")

# No hospital name, booking number, hospital branding or claim of institutional approval.
st.caption(education.COMMON_GUIDANCE[0])
with st.expander("교육내용 근거"):
    for source in education.GUIDELINE_SOURCES:
        st.markdown(f"- {source}")
    st.caption("세부 복약·식사·기기·맥박 측정의 보충 근거는 각 교육항목의 출처를 확인하세요.")

render_bottom_navigation()
scroll_to_page_top()
