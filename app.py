# AF patient education chatbot UI
# Version: v20261002_11
# Updated: 2026-10-02

import os
import html
import streamlit as st
from openai import OpenAI
from modules import MODULES, START_NOTICE, FREE_QUESTION_NOTICE

st.set_page_config(
    page_title="심방세동 AI 기반 챗봇 교육",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MODULE_ORDER = ["1", "2", "3", "4", "5", "6", "7", "8"]
FONT_LEVELS = [1.00, 1.15, 1.30]


def init_state():
    defaults = {
        "view": "home",            # home / module / content / free / answer
        "module": None,
        "item_id": None,
        "font_level": 0,
        "free_return": None,
        "answer_return": None,
        "answer_question": None,
        "answer_text": None,
        "answer_context": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()
font_scale = FONT_LEVELS[st.session_state.font_level]


# =========================================================
# 스타일
# =========================================================
CSS = r"""
<style>
html { font-size: __FONT_SIZE__px !important; }

:root {
    --page-bg: #F4F8FC;
    --ink: #173B55;
    --muted: #607488;
    --card: #FFFFFF;
    --teal-bg: #E6F3F1;
    --teal-border: #B9D8D2;
    --teal-ink: #174B4A;
    --teal-hover: #D8ECE8;
    --line: rgba(23, 59, 85, .12);
}

.stApp { background: var(--page-bg); }
.block-container {
    max-width: 1100px;
    padding-top: 2.7rem;
    padding-bottom: 12.5rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

/* ---------- 상단 타이틀 ---------- */
.title-wrap {
    display:flex;
    align-items:center;
    gap:.7rem;
    width:100%;
    margin:0 0 .2rem 0;
}
.ecg-icon { width:3.2rem; height:3.2rem; flex:0 0 auto; }
.title-texts { min-width:0; flex:1 1 auto; }
.main-title {
    color:var(--ink);
    font-size:clamp(2rem, 5.5vw, 3.35rem);
    font-weight:850;
    line-height:1.05;
    letter-spacing:-.045em;
    margin:0;
}
.main-subtitle {
    color:var(--muted);
    font-size:clamp(.98rem, 2.8vw, 1.18rem);
    line-height:1.25;
    margin-top:.18rem;
    font-weight:520;
}

/* 제목 아래 설명 + 글자 조절 + 챗봇 바로가기 */
.header-helper-text {
    color:#506779;
    font-size:.98rem;
    line-height:1.55;
    margin:0;
}
[class*="st-key-top_helper_bar_"] { margin-bottom:.35rem !important; }
[class*="st-key-top_helper_bar_"] [data-testid="stHorizontalBlock"] {
    flex-wrap:nowrap !important;
    align-items:center !important;
    gap:.35rem !important;
}
[class*="st-key-top_helper_bar_"] [data-testid="stColumn"]:first-child {
    flex:1 1 auto !important; min-width:0 !important; width:auto !important;
}
[class*="st-key-top_helper_bar_"] [data-testid="stColumn"]:nth-child(2),
[class*="st-key-top_helper_bar_"] [data-testid="stColumn"]:nth-child(3) {
    flex:0 0 2.35rem !important; min-width:2.35rem !important; width:2.35rem !important;
}
[class*="st-key-top_helper_bar_"] [data-testid="stColumn"]:last-child {
    flex:0 0 3rem !important; min-width:3rem !important; width:3rem !important;
}
[class*="st-key-top_font_"] button {
    min-height:2.25rem !important; height:2.25rem !important; width:2.25rem !important;
    padding:0 !important; border-radius:.7rem !important;
    text-align:center !important; justify-content:center !important;
    font-size:.78rem !important;
}
[class*="st-key-top_font_"] button p { text-align:center !important; }
[class*="st-key-top_chatbot_"] button {
    min-height:2.75rem !important; height:2.75rem !important; width:2.75rem !important;
    padding:0 !important; border:none !important; border-radius:.8rem !important;
    background-color:transparent !important;
    background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0OCA0OCI+PHJlY3QgeD0iMiIgeT0iMiIgd2lkdGg9IjQ0IiBoZWlnaHQ9IjQ0IiByeD0iMTEiIGZpbGw9IiNmZjhhMDAiLz48bGluZSB4MT0iMjQiIHkxPSIxMCIgeDI9IjI0IiB5Mj0iMTQiIHN0cm9rZT0iIzE3MTcxNyIgc3Ryb2tlLXdpZHRoPSIyLjQiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjxjaXJjbGUgY3g9IjI0IiBjeT0iOC41IiByPSIyLjEiIGZpbGw9IiMxNzE3MTciLz48cmVjdCB4PSIxNCIgeT0iMTUiIHdpZHRoPSIyMCIgaGVpZ2h0PSIxOCIgcng9IjQiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzE3MTcxNyIgc3Ryb2tlLXdpZHRoPSIyLjgiLz48cmVjdCB4PSIxMC41IiB5PSIyMCIgd2lkdGg9IjMuNSIgaGVpZ2h0PSI4IiByeD0iMS41IiBmaWxsPSIjMTcxNzE3Ii8+PHJlY3QgeD0iMzQiIHk9IjIwIiB3aWR0aD0iMy41IiBoZWlnaHQ9IjgiIHJ4PSIxLjUiIGZpbGw9IiMxNzE3MTciLz48Y2lyY2xlIGN4PSIyMCIgY3k9IjIzIiByPSIyIiBmaWxsPSIjMTcxNzE3Ii8+PGNpcmNsZSBjeD0iMjgiIGN5PSIyMyIgcj0iMiIgZmlsbD0iIzE3MTcxNyIvPjxwYXRoIGQ9Ik0yMCAyOC41IEgyOCIgc3Ryb2tlPSIjMTcxNzE3IiBzdHJva2Utd2lkdGg9IjIuNCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PHBhdGggZD0iTTE4IDM2IEgzMCIgc3Ryb2tlPSIjMTcxNzE3IiBzdHJva2Utd2lkdGg9IjIuNiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PC9zdmc+") !important;
    background-repeat:no-repeat !important;
    background-position:center !important;
    background-size:2.65rem 2.65rem !important;
}
[class*="st-key-top_chatbot_"] button p,
[class*="st-key-top_chatbot_"] button [data-testid="stMarkdownContainer"] {
    font-size:0 !important; line-height:0 !important; color:transparent !important;
}

/* Streamlit 모바일 사이드바 열기: >> 대신 '이전' 표시, 실제 목록은 활성 */
[data-testid="stSidebarCollapsedControl"] svg { display:none !important; }
[data-testid="stSidebarCollapsedControl"]::after {
    content:"이전";
    font-size:.84rem;
    font-weight:750;
    white-space:nowrap;
    color:var(--ink);
}

/* ---------- 공통 버튼 ---------- */
div.stButton > button {
    border-radius:16px;
    font-weight:700;
    text-align:left !important;
    justify-content:flex-start !important;
}
div.stButton > button p { width:100%; margin:0; text-align:left !important; }

/* ---------- 홈: 2열 x 4행 대주제 ---------- */
[class*="st-key-home_topic_"] button {
    min-height:4.45rem !important;
    background:var(--teal-bg) !important;
    color:var(--teal-ink) !important;
    border:1px solid var(--teal-border) !important;
    box-shadow:0 4px 14px rgba(23,75,74,.07) !important;
    padding:.8rem .85rem !important;
    line-height:1.25 !important;
    font-size:1rem !important;
}
[class*="st-key-home_topic_"] button:hover {
    background:var(--teal-hover) !important;
    border-color:#9CC9C1 !important;
}
.home-grid-wrap { margin-top:.25rem; }

/* ---------- 소주제 목록 ---------- */
.module-title {
    color:var(--ink);
    font-size:clamp(1.8rem, 5vw, 3rem);
    font-weight:850;
    line-height:1.12;
    letter-spacing:-.035em;
    margin:.18rem 0 .55rem 0;
}
[class*="st-key-subtopic_"] button {
    min-height:4rem !important;
    background:#EFF6FB !important;
    color:#23577B !important;
    border:1px solid #C8DBEA !important;
    padding:.75rem 1rem !important;
    box-shadow:0 2px 9px rgba(35,87,123,.05) !important;
    font-size:1rem !important;
}
.module-back-wrap { margin-top:.45rem; }
[class*="st-key-module_back_"] button {
    width:auto !important;
    min-height:2.65rem !important;
    padding:.45rem 1rem !important;
    background:#fff !important;
    color:var(--ink) !important;
    border:1px solid #D7E1E8 !important;
}

/* ---------- 교육내용 상세 ---------- */
.content-module-label {
    color:#506779;
    font-size:1rem;
    margin:.2rem 0 .35rem 0;
}
.content-card {
    background:#fff;
    border:1px solid #D8E2EA;
    border-radius:24px;
    padding:1.35rem 1.35rem 1.05rem 1.35rem;
    box-shadow:0 7px 24px rgba(30,64,91,.06);
}
.content-count {
    display:inline-block;
    color:#2D6893;
    background:#EEF5FF;
    border-radius:999px;
    padding:.35rem .7rem;
    font-weight:750;
    font-size:.9rem;
    margin-bottom:.7rem;
}
.content-title {
    color:var(--ink);
    font-size:clamp(1.8rem, 5.5vw, 3rem);
    font-weight:850;
    line-height:1.15;
    letter-spacing:-.04em;
    margin:.15rem 0 .75rem 0;
}
.education-answer { color:#263F50; font-size:1.05rem; line-height:1.9; text-align:left; }
.education-source {
    margin-top:1rem; padding-top:.8rem; border-top:1px solid var(--line);
    color:#65798A; font-size:.82rem; line-height:1.5;
}
.content-nav { margin-top:.55rem; }
[class*="st-key-prev_content_"] button,
[class*="st-key-next_content_"] button {
    min-height:3.3rem !important;
    justify-content:center !important;
    text-align:center !important;
}
[class*="st-key-prev_content_"] button p,
[class*="st-key-next_content_"] button p { text-align:center !important; }
[class*="st-key-prev_content_"] button {
    background:#fff !important; color:var(--ink) !important; border:1px solid #D1DDE6 !important;
}
[class*="st-key-next_content_"] button {
    background:#2D6D80 !important; color:white !important; border:1px solid #2D6D80 !important;
}

/* ---------- 자유질문 ---------- */
.free-panel {
    background:#fff;
    border:1px solid #D8E2EA;
    border-radius:22px;
    padding:1rem 1rem .75rem 1rem;
    margin-top:.7rem;
    box-shadow:0 5px 18px rgba(30,64,91,.05);
}
.free-question-title {
    display:flex; align-items:center; gap:.55rem;
    color:var(--ink); font-size:1.25rem; font-weight:800; margin:0 0 .15rem 0;
}
.chatbot-icon { width:2rem; height:2rem; flex:0 0 auto; }
.free-question-note {
    color:#65798A; font-size:.78rem; line-height:1.45; margin:.12rem 0 .5rem 0;
}

/* ChatGPT 느낌의 원형 위쪽 화살표 전송 버튼 */
[data-testid="stChatInput"] { width:100% !important; position:relative !important; }
[data-testid="stChatInput"] textarea { padding-right:3.2rem !important; }
[data-testid="stChatInputSubmitButton"] {
    position:absolute !important; right:.55rem !important; top:50% !important;
    transform:translateY(-50%) !important;
    min-height:2.35rem !important; height:2.35rem !important; width:2.35rem !important;
    padding:0 !important; border:none !important; border-radius:50% !important;
    background:#203A4A !important;
    display:flex !important; align-items:center !important; justify-content:center !important;
}
[data-testid="stChatInputSubmitButton"] svg { display:none !important; }
[data-testid="stChatInputSubmitButton"]::after {
    content:"↑"; color:#fff; font-size:1.35rem; line-height:1; font-weight:850;
}

/* ---------- AI 답변 전용 화면 ---------- */
.answer-page-title {
    color:var(--ink); font-size:1.55rem; font-weight:850; margin:.25rem 0 .65rem 0;
}
.question-card, .answer-card {
    background:#fff; border:1px solid #D8E2EA; border-radius:20px;
    padding:1rem 1.05rem; margin:.5rem 0;
    box-shadow:0 5px 16px rgba(30,64,91,.05);
}
.qa-label { color:#607488; font-size:.8rem; font-weight:800; margin-bottom:.35rem; }
.question-text { color:var(--ink); font-size:1.05rem; font-weight:700; line-height:1.6; }
.answer-text { color:#263F50; font-size:1.03rem; line-height:1.8; }
.answer-note {
    margin-top:.8rem; padding-top:.65rem; border-top:1px solid var(--line);
    color:#65798A; font-size:.8rem; line-height:1.45;
}
[class*="st-key-answer_back_"] button,
[class*="st-key-answer_home_"] button {
    min-height:3.15rem !important; justify-content:center !important; text-align:center !important;
}
[class*="st-key-answer_back_"] button p,
[class*="st-key-answer_home_"] button p { text-align:center !important; }

/* ---------- 하단 고정 네비게이션: Streamlit 플로팅 아이콘과 겹치지 않도록 위로 ---------- */
[class*="st-key-bottom_nav_"] {
    position:fixed !important;
    left:50% !important;
    transform:translateX(-50%) !important;
    bottom:calc(88px + env(safe-area-inset-bottom)) !important;
    width:min(660px, calc(100vw - 28px)) !important;
    z-index:999 !important;
    background:rgba(255,255,255,.96) !important;
    border:1px solid #D8E2EA !important;
    border-radius:22px !important;
    padding:.55rem !important;
    box-shadow:0 9px 28px rgba(24,54,74,.15) !important;
    backdrop-filter:blur(10px);
}
[class*="st-key-bottom_nav_"] [data-testid="stHorizontalBlock"] {
    flex-wrap:nowrap !important; gap:.45rem !important;
}
[class*="st-key-bottom_nav_"] button {
    min-height:3.55rem !important;
    justify-content:center !important; text-align:center !important;
    border:none !important; box-shadow:none !important;
    font-size:1rem !important;
}
[class*="st-key-bottom_nav_"] button p { text-align:center !important; }
[class*="st-key-bottom_edu_"] button { background:#E8F1FF !important; color:#245F9B !important; }
[class*="st-key-bottom_chat_"] button { background:#F7F9FB !important; color:#4D6273 !important; }

/* 일반적인 Streamlit 상단 여백/구분선 최소화 */
hr { margin:.55rem 0 !important; }

@media (max-width: 600px) {
    .block-container {
        padding-top:2.45rem;
        padding-left:.72rem;
        padding-right:.72rem;
        padding-bottom:12.5rem;
    }
    .title-wrap { gap:.55rem; }
    .ecg-icon { width:3.05rem; height:3.05rem; }
    .main-title { font-size:2.18rem; }
    .main-subtitle { font-size:1rem; }
    .header-helper-text { font-size:.9rem; }
    [class*="st-key-top_helper_bar_"] [data-testid="stColumn"]:nth-child(2),
    [class*="st-key-top_helper_bar_"] [data-testid="stColumn"]:nth-child(3) {
        flex-basis:2rem !important; min-width:2rem !important; width:2rem !important;
    }
    [class*="st-key-top_helper_bar_"] [data-testid="stColumn"]:last-child {
        flex-basis:2.8rem !important; min-width:2.8rem !important; width:2.8rem !important;
    }
    [class*="st-key-top_font_"] button {
        min-height:2rem !important; height:2rem !important; width:2rem !important;
        font-size:.68rem !important;
    }
    [class*="st-key-home_topic_"] button {
        min-height:4.25rem !important;
        padding:.65rem .62rem !important;
        font-size:.86rem !important;
        border-radius:15px !important;
    }
    .module-title { font-size:2rem; margin-top:.05rem; }
    [class*="st-key-subtopic_"] button {
        min-height:3.7rem !important;
        font-size:.94rem !important;
        padding:.6rem .85rem !important;
    }
    .content-card { padding:1rem .95rem .85rem .95rem; border-radius:21px; }
    .content-title { font-size:2.05rem; }
    .education-answer { font-size:1rem; line-height:1.82; }
    [class*="st-key-bottom_nav_"] {
        bottom:calc(82px + env(safe-area-inset-bottom)) !important;
        width:calc(100vw - 24px) !important;
        border-radius:20px !important;
    }
}
</style>
"""
st.markdown(CSS.replace("__FONT_SIZE__", f"{16 * font_scale:.2f}"), unsafe_allow_html=True)


# =========================================================
# 이동 / 상태
# =========================================================
def go_home():
    st.session_state.view = "home"
    st.session_state.module = None
    st.session_state.item_id = None


def go_module(mid):
    st.session_state.view = "module"
    st.session_state.module = mid
    st.session_state.item_id = None


def go_content(mid, item_id):
    st.session_state.view = "content"
    st.session_state.module = mid
    st.session_state.item_id = item_id


def go_free():
    st.session_state.free_return = (
        st.session_state.view,
        st.session_state.module,
        st.session_state.item_id,
    )
    st.session_state.view = "free"


def go_back_from_free():
    prev = st.session_state.free_return or ("home", None, None)
    st.session_state.view, st.session_state.module, st.session_state.item_id = prev
    st.session_state.free_return = None


def start_answer(question, context=None):
    st.session_state.answer_return = (
        st.session_state.view,
        st.session_state.module,
        st.session_state.item_id,
    )
    st.session_state.answer_question = question
    st.session_state.answer_context = context
    st.session_state.answer_text = None
    st.session_state.view = "answer"


def go_back_from_answer():
    prev = st.session_state.answer_return or ("home", None, None)
    st.session_state.view, st.session_state.module, st.session_state.item_id = prev
    st.session_state.answer_question = None
    st.session_state.answer_text = None
    st.session_state.answer_context = None
    st.session_state.answer_return = None


def change_font_size(delta):
    new_level = st.session_state.font_level + delta
    st.session_state.font_level = max(0, min(len(FONT_LEVELS) - 1, new_level))


# =========================================================
# OpenAI
# =========================================================
def get_client():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return OpenAI(api_key=key) if key else None


def all_fixed_content():
    chunks = []
    for mid in MODULE_ORDER:
        m = MODULES[mid]
        lines = [f"[{mid}. {m['name']}]" ]
        for item in m["items"]:
            lines.append(f"{item['id']}. {item['title']}\n{item['answer']}\n출처: {item['source']}")
        chunks.append("\n\n".join(lines))
    return "\n\n".join(chunks)


def generate_answer(user_text, current_context=None):
    client = get_client()
    if not client:
        return "현재 AI 답변 기능을 사용할 수 없습니다. 교육내용을 참고하거나 담당 의료진과 상담해 주세요."

    context_note = f"\n현재 사용자가 보고 있던 교육항목: {current_context}\n" if current_context else ""
    system = f"""
당신은 심방세동 환자를 위한 교육 챗봇입니다.
아래 68개 고정 교육내용을 우선적인 답변 근거로 사용하여 환자가 이해하기 쉬운 한국어로 간결하게 답변합니다.
{context_note}
개인의 진단을 하지 않습니다.
약물의 시작·중단·용량 변경을 지시하지 않습니다.
개인별 시술 여부를 결정하지 않습니다.
고정 교육내용으로 답하기 어렵거나 개인 상태 확인이 필요한 경우 담당 의료진과 상담하도록 안내합니다.
AI 답변은 일반적인 교육정보이며 진료를 대신하지 않습니다.

[고정 교육내용]
{all_fixed_content()}
"""
    try:
        r = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_text},
            ],
        )
        ans = (r.output_text or "").strip()
        return ans or "답변을 생성하지 못했습니다. 담당 의료진과 상담해 주세요."
    except Exception:
        return "현재 AI 답변을 불러오지 못했습니다. 교육내용을 참고하거나 담당 의료진과 상담해 주세요."


# =========================================================
# 공통 상단
# =========================================================
def render_title():
    st.markdown(
        """
        <div class="title-wrap">
            <svg class="ecg-icon" viewBox="0 0 48 48" aria-hidden="true">
                <rect x="3" y="3" width="42" height="42" rx="9" fill="#e53935"/>
                <polyline points="8,25 14,25 17,20 21,31 26,14 31,28 34,25 40,25"
                    fill="none" stroke="#ffffff" stroke-width="3.2"
                    stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="title-texts">
                <div class="main-title">심방세동</div>
                <div class="main-subtitle">AI 기반 챗봇 교육</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_helper_bar(scope_key):
    with st.container(key=f"top_helper_bar_{scope_key}"):
        text_col, minus_col, plus_col, icon_col = st.columns([0.79, 0.07, 0.07, 0.07], gap="small")
        with text_col:
            st.markdown(
                '<div class="header-helper-text">심방세동 교육주제를 선택하고, 궁금한 내용은 챗봇에게 질문해 주세요.</div>',
                unsafe_allow_html=True,
            )
        with minus_col:
            if st.button(
                "가−", key=f"top_font_minus_{scope_key}", help="글자 작게",
                use_container_width=True, disabled=st.session_state.font_level == 0,
            ):
                change_font_size(-1)
                st.rerun()
        with plus_col:
            if st.button(
                "가+", key=f"top_font_plus_{scope_key}", help="글자 크게",
                use_container_width=True,
                disabled=st.session_state.font_level == len(FONT_LEVELS) - 1,
            ):
                change_font_size(1)
                st.rerun()
        with icon_col:
            if st.button(
                "챗봇", key=f"top_chatbot_{scope_key}", help="챗봇 질문",
                use_container_width=True,
            ):
                go_free()
                st.rerun()


# =========================================================
# 자유질문
# =========================================================
def chatbot_svg():
    return """
    <svg class="chatbot-icon" viewBox="0 0 48 48" aria-hidden="true">
        <rect x="2" y="2" width="44" height="44" rx="11" fill="#ff8a00"/>
        <line x1="24" y1="10" x2="24" y2="14" stroke="#171717" stroke-width="2.4" stroke-linecap="round"/>
        <circle cx="24" cy="8.5" r="2.1" fill="#171717"/>
        <rect x="14" y="15" width="20" height="18" rx="4" fill="none" stroke="#171717" stroke-width="2.8"/>
        <rect x="10.5" y="20" width="3.5" height="8" rx="1.5" fill="#171717"/>
        <rect x="34" y="20" width="3.5" height="8" rx="1.5" fill="#171717"/>
        <circle cx="20" cy="23" r="2" fill="#171717"/>
        <circle cx="28" cy="23" r="2" fill="#171717"/>
        <path d="M20 28.5 H28" stroke="#171717" stroke-width="2.4" stroke-linecap="round"/>
        <path d="M18 36 H30" stroke="#171717" stroke-width="2.6" stroke-linecap="round"/>
    </svg>
    """


def render_free_question(scope, current_context=None, standalone=False):
    st.markdown('<div class="free-panel">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="free-question-title">{chatbot_svg()}<span>자유롭게 질문하세요.</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="free-question-note">질문은 답변 생성을 위해 외부 AI 서비스로 전송됩니다. 개인정보나 본인을 알아볼 수 있는 진료자료는 입력하지 마세요.</div>',
        unsafe_allow_html=True,
    )
    user = st.chat_input(
        placeholder="궁금한 내용을 입력하세요.",
        key=f"chat_input_{scope}",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if user and user.strip():
        start_answer(user.strip(), context=current_context)
        st.rerun()


# =========================================================
# 교육내용 네비게이션
# =========================================================
def get_item_index(mid, item_id):
    items = MODULES[mid]["items"]
    for idx, item in enumerate(items):
        if item["id"] == item_id:
            return idx
    return None


# =========================================================
# 사이드바 이동 목록 (활성)
# =========================================================
with st.sidebar:
    st.markdown("### 주제 목록")
    if st.button("첫 화면", key="nav_home", use_container_width=True):
        go_home()
        st.rerun()
    for mid in MODULE_ORDER:
        m = MODULES[mid]
        if st.button(f"{mid}. {m['name']}", key=f"nav_module_{mid}", use_container_width=True):
            go_module(mid)
            st.rerun()


# =========================================================
# 렌더링
# =========================================================
render_title()
helper_scope = f"{st.session_state.view}_{st.session_state.module or 'home'}_{st.session_state.item_id or 'none'}"
render_top_helper_bar(helper_scope)


if st.session_state.view == "home":
    # '교육 주제' / '8개 주제' 제목은 사용하지 않음.
    st.markdown('<div class="home-grid-wrap"></div>', unsafe_allow_html=True)
    for row_start in range(0, len(MODULE_ORDER), 2):
        cols = st.columns(2, gap="small")
        for col_idx, mid in enumerate(MODULE_ORDER[row_start:row_start + 2]):
            m = MODULES[mid]
            with cols[col_idx]:
                if st.button(
                    f"{mid}. {m['name']}  ›",
                    key=f"home_topic_{mid}",
                    use_container_width=True,
                ):
                    go_module(mid)
                    st.rerun()

    # 첫 화면에서 교육주제 아래 자유질문 유지
    render_free_question("home")


elif st.session_state.view == "module":
    mid = st.session_state.module
    m = MODULES[mid]

    # '주제 01' 및 하위주제 개수 설명 삭제. 제목 자체에 번호 표시.
    st.markdown(
        f'<div class="module-title">{mid}. {html.escape(m["name"])}</div>',
        unsafe_allow_html=True,
    )

    for item in m["items"]:
        if st.button(
            f"{item['id']}. {item['title']}  ›",
            key=f"subtopic_{item['id']}",
            use_container_width=True,
        ):
            go_content(mid, item["id"])
            st.rerun()

    # 주제목록 아래 왼쪽에 이전 버튼
    with st.container(key=f"module_back_wrap_{mid}"):
        if st.button("← 이전", key=f"module_back_{mid}"):
            go_home()
            st.rerun()


elif st.session_state.view == "content":
    mid = st.session_state.module
    m = MODULES[mid]
    idx = get_item_index(mid, st.session_state.item_id)
    if idx is None:
        go_module(mid)
        st.rerun()
    item = m["items"][idx]
    total = len(m["items"])

    # 기존 상단 '← / 교육내용 / 첫 화면' 행은 제거.
    st.markdown(
        f'<div class="content-module-label">{mid}. {html.escape(m["name"])}</div>',
        unsafe_allow_html=True,
    )

    answer_html = html.escape(item["answer"]).replace("\n\n", "<br><br>").replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="content-card">
            <div class="content-count">{idx + 1:02d} / {total:02d}</div>
            <div class="content-title">{html.escape(item['title'])}</div>
            <div class="education-answer">{answer_html}</div>
            <div class="education-source">출처: {html.escape(item['source'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 하위주제 목록 삭제 → 이전 내용 / 다음 내용
    st.markdown('<div class="content-nav"></div>', unsafe_allow_html=True)
    prev_col, next_col = st.columns(2, gap="small")
    with prev_col:
        if idx > 0:
            prev_item = m["items"][idx - 1]
            if st.button("← 이전 내용", key=f"prev_content_{item['id']}", use_container_width=True):
                go_content(mid, prev_item["id"])
                st.rerun()
        else:
            st.button("← 이전 내용", key=f"prev_content_{item['id']}", use_container_width=True, disabled=True)
    with next_col:
        if idx < total - 1:
            next_item = m["items"][idx + 1]
            if st.button("다음 내용 →", key=f"next_content_{item['id']}", use_container_width=True):
                go_content(mid, next_item["id"])
                st.rerun()
        else:
            st.button("다음 내용 →", key=f"next_content_{item['id']}", use_container_width=True, disabled=True)

    # 교육내용 설명란 바로 아래 자유질문
    render_free_question(
        f"content_{item['id']}",
        current_context=f"{item['id']}. {item['title']}",
    )


elif st.session_state.view == "free":
    st.markdown('<div class="answer-page-title">챗봇 질문</div>', unsafe_allow_html=True)
    render_free_question("free_page", standalone=True)

    if st.button("← 이전", key="free_back"):
        go_back_from_free()
        st.rerun()


elif st.session_state.view == "answer":
    question = st.session_state.answer_question or ""

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
        # API 응답 동안 화면에 표시되는 확정 문구
        with st.spinner("답변을 준비하고 있습니다. 잠시만 기다려 주세요."):
            st.session_state.answer_text = generate_answer(
                question,
                current_context=st.session_state.answer_context,
            )
        st.rerun()

    answer_html = html.escape(st.session_state.answer_text or "").replace("\n\n", "<br><br>").replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="answer-card">
            <div class="qa-label">AI 답변</div>
            <div class="answer-text">{answer_html}</div>
            <div class="answer-note">AI 답변은 참고용이며, 진단·치료 결정은 담당 의료진과 상담하세요.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    back_col, home_col = st.columns(2, gap="small")
    with back_col:
        if st.button("← 이전", key="answer_back", use_container_width=True):
            go_back_from_answer()
            st.rerun()
    with home_col:
        if st.button("처음으로", key="answer_home", use_container_width=True):
            st.session_state.answer_question = None
            st.session_state.answer_text = None
            st.session_state.answer_context = None
            st.session_state.answer_return = None
            go_home()
            st.rerun()


# =========================================================
# 하단 고정 네비게이션
# 답변 전용 화면에서는 명시적인 '이전/처음으로' 버튼이 있으므로 숨김.
# =========================================================
if st.session_state.view != "answer":
    with st.container(key=f"bottom_nav_{st.session_state.view}"):
        edu_col, chat_col = st.columns(2, gap="small")
        with edu_col:
            if st.button("▦  교육 주제", key=f"bottom_edu_{st.session_state.view}", use_container_width=True):
                go_home()
                st.rerun()
        with chat_col:
            if st.button("▢  챗봇 질문", key=f"bottom_chat_{st.session_state.view}", use_container_width=True):
                go_free()
                st.rerun()


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
