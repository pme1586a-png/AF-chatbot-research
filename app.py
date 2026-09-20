import os
import streamlit as st
from openai import OpenAI
from modules import MODULES

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="심방세동 AI 챗봇 교육",
    page_icon="🫀",
    layout="wide"
)

# =========================================================
# 화면 스타일
# =========================================================
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* 제목 */
    .title-wrap {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        white-space: nowrap;
        width: 100%;
        margin-bottom: 0.3rem;
    }

    .ecg-icon {
        width: 42px;
        min-width: 42px;
        height: 26px;
        flex-shrink: 0;
    }

    .main-title {
        font-size: clamp(1.1rem, 4vw, 2rem);
        font-weight: 700;
        line-height: 1.2;
        white-space: nowrap;
        margin: 0;
    }

    @media (max-width: 480px) {
        .block-container {
            padding-left: 0.65rem;
            padding-right: 0.65rem;
        }

        .ecg-icon {
            width: 32px;
            min-width: 32px;
            height: 22px;
        }

        .main-title {
            font-size: 1.15rem;
        }
    }

    @media (max-width: 360px) {
        .ecg-icon {
            width: 28px;
            min-width: 28px;
        }

        .main-title {
            font-size: 1rem;
        }
    }

    /* 버튼 왼쪽 정렬 */
    div.stButton > button {
        min-height: 3.2rem;
        border-radius: 14px;
        font-weight: 650;
        text-align: left !important;
        justify-content: flex-start !important;
    }

    div.stButton > button p {
        width: 100% !important;
        margin: 0 !important;
        text-align: left !important;
    }

    div[data-testid="stButton"] > button,
    div[data-testid="stButton"] > button > div,
    div[data-testid="stButton"] > button [data-testid="stMarkdownContainer"],
    div[data-testid="stButton"] > button [data-testid="stMarkdownContainer"] p,
    .stButton button,
    .stButton button > div,
    .stButton button p {
        text-align: left !important;
        justify-content: flex-start !important;
    }

    div[data-testid="stButton"] > button [data-testid="stMarkdownContainer"],
    .stButton button [data-testid="stMarkdownContainer"] {
        width: 100% !important;
    }

    [data-testid="stSidebar"] div.stButton > button {
        font-size: 0.98rem;
    }

    .education-answer {
        font-size: 1.08rem;
        line-height: 1.85;
        text-align: left;
    }

    .education-source {
        margin-top: 1rem;
        font-size: 0.84rem;
        line-height: 1.55;
        opacity: 0.72;
        text-align: left;
    }

    .hospital {
        padding: 14px 16px;
        border: 1px solid #ddd;
        border-radius: 14px;
        margin-top: 14px;
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 제목: 심전도 모양 + 심방세동 AI 챗봇 교육
# =========================================================
st.markdown(
    """
    <div class="title-wrap">
        <svg class="ecg-icon" viewBox="0 0 100 50" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <polyline
                points="0,25 18,25 25,18 32,35 42,5 52,42 61,25 100,25"
                fill="none"
                stroke="#e53935"
                stroke-width="6"
                stroke-linecap="round"
                stroke-linejoin="round"
            />
        </svg>
        <div class="main-title">심방세동 AI 챗봇 교육</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("심방세동 환자를 위한 교육용 챗봇 · 8개 교육 주제 + 추가 자유질문")

# =========================================================
# 세션 상태
# =========================================================
if "module" not in st.session_state:
    st.session_state.module = None

if "question" not in st.session_state:
    st.session_state.question = None

if "chat" not in st.session_state:
    st.session_state.chat = []

# =========================================================
# OpenAI 연결
# =========================================================
def get_client():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return OpenAI(api_key=key) if key else None

# =========================================================
# 화면 이동 함수
# =========================================================
def select_module(mid):
    st.session_state.module = mid
    st.session_state.question = None
    st.session_state.chat = []

def select_question(i):
    st.session_state.question = i
    st.session_state.chat = []

def go_home():
    st.session_state.module = None
    st.session_state.question = None
    st.session_state.chat = []

# =========================================================
# 사이드바
# =========================================================
with st.sidebar:
    if st.button("🏠 첫 화면으로", key="go_home", use_container_width=True):
        go_home()
        st.rerun()

    st.header("교육 주제")

    for mid, m in MODULES.items():
        if st.button(
            f"{m['icon']} {mid}. {m['name']}",
            key=f"sidebar_module_{mid}",
            use_container_width=True
        ):
            select_module(mid)
            st.rerun()

    st.divider()
    st.markdown("**☎ 병원 이용 안내**")
    st.markdown(
        "전화예약센터 **1688-6114**  \n"
        "응급실 안내 **031-219-7777**"
    )
    st.caption("응급상황은 119 또는 가까운 응급실을 우선 이용하세요.")

# =========================================================
# 첫 화면
# =========================================================
if st.session_state.module is None:
    st.subheader("원하는 교육 주제를 선택하세요")

    cols = st.columns(2)

    for idx, (mid, m) in enumerate(MODULES.items()):
        with cols[idx % 2]:
            if st.button(
                f"{m['icon']}  {mid}. {m['name']}",
                key=f"home_module_{mid}",
                use_container_width=True
            ):
                select_module(mid)
                st.rerun()

    st.info(
        "교육내용은 대한부정맥학회 2024 심방세동 진료지침, "
        "2024 ESC 및 2023 ACC/AHA/ACCP/HRS 심방세동 진료지침을 중심으로 구성했습니다."
    )

    st.divider()
    st.subheader("💬 추가로 궁금한 내용을 자유롭게 질문해 주세요")
    st.caption("개인 진단·처방·약물 용량 변경·개인별 시술 결정은 제공하지 않습니다.")

    client = get_client()

    home_q_col, home_send_col = st.columns([0.84, 0.16], gap="small")

    with home_q_col:
        user = st.text_input(
            "자유질문",
            placeholder="예: 심방세동은 왜 생기나요?",
            key="home_chat_input",
            label_visibility="collapsed"
        )

    with home_send_col:
        home_send = st.button(
            "질문하기",
            key="home_send",
            use_container_width=True
        )

    if home_send and user.strip():
        st.session_state.chat.append(("user", user))

        if client:
            all_fixed = "\n\n".join(
                [
                    f"[{m2['name']}]\n"
                    + "\n".join(
                        [f"Q: {q}\nA: {a}" for q, a in m2["questions"]]
                    )
                    for m2 in MODULES.values()
                ]
            )

            system = f"""
당신은 심방세동 환자 교육 챗봇입니다.

아래 고정 교육내용과
대한부정맥학회 2024 심방세동 진료지침,
2024 ESC 심방세동 진료지침,
2023 ACC/AHA/ACCP/HRS 심방세동 진료지침 범위에서
환자가 이해하기 쉬운 한국어로 답변합니다.

개인의 진단을 하지 않습니다.
약물의 시작, 중단, 용량 변경을 지시하지 않습니다.
개인별 시술 여부를 결정하지 않습니다.
근거가 부족하거나 개인 상태 확인이 필요한 경우 담당 의료진에게 문의하도록 안내합니다.
응급 증상이 의심되는 경우 챗봇 답변보다 119 또는 응급실 이용을 우선 안내합니다.

아주대학교병원 전화예약센터는 1688-6114,
응급실 안내는 031-219-7777입니다.

가능한 한 간결하고 이해하기 쉽게 설명합니다.

[고정 교육내용]

{all_fixed}
"""

            try:
                r = client.responses.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
                    input=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ]
                )
                ans = (r.output_text or "").strip()
                if not ans:
                    ans = "답변을 생성하지 못했습니다. 담당 의료진에게 문의해 주세요."
            except Exception:
                ans = (
                    "현재 추가 질문 답변을 불러오지 못했습니다. "
                    "교육 주제의 고정 교육내용을 참고하거나 담당 의료진에게 문의해 주세요."
                )
        else:
            ans = (
                "현재 OPENAI_API_KEY가 설정되지 않아 자유질문 AI 답변은 사용할 수 없습니다. "
                "교육 주제의 고정 교육내용은 정상적으로 이용할 수 있습니다."
            )

        st.session_state.chat.append(("assistant", ans))
        st.rerun()

    for role, text_chat in st.session_state.chat[-8:]:
        with st.chat_message(role):
            st.markdown(text_chat)

# =========================================================
# 교육 주제 화면
# =========================================================
else:
    mid = st.session_state.module
    m = MODULES[mid]

    st.header(f"{m['icon']} {mid}. {m['name']}")
    st.write("궁금한 질문을 선택하면 오른쪽에 교육내용이 표시됩니다.")

    question_col, answer_col = st.columns([0.42, 0.58], gap="large")

    with question_col:
        st.subheader("📋 교육 질문")

        for i, (q, a) in enumerate(m["questions"]):
            if st.button(
                q,
                key=f"question_{mid}_{i}",
                use_container_width=True
            ):
                select_question(i)
                st.rerun()

    with answer_col:
        st.subheader("📖 교육 내용")

        if st.session_state.question is None:
            st.info("왼쪽에서 궁금한 질문을 선택해 주세요.")
        else:
            i = st.session_state.question
            q, a = m["questions"][i]

            st.markdown(f"### {q}")

            st.markdown(
                f"<div class='education-answer'>{a}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div class='education-source'>근거: {m['source']}</div>",
                unsafe_allow_html=True
            )

    st.divider()
    st.subheader("💬 추가로 궁금한 내용을 자유롭게 질문해 주세요")
    st.caption("개인 진단·처방·약물 용량 변경·개인별 시술 결정은 제공하지 않습니다.")

    client = get_client()

    module_q_col, module_send_col = st.columns([0.84, 0.16], gap="small")

    with module_q_col:
        user = st.text_input(
            "자유질문",
            placeholder="예: 시술 후에도 항응고제를 계속 먹어야 하나요?",
            key=f"module_chat_input_{mid}_{st.session_state.question}",
            label_visibility="collapsed"
        )

    with module_send_col:
        module_send = st.button(
            "질문하기",
            key=f"module_send_{mid}_{st.session_state.question}",
            use_container_width=True
        )

    if module_send and user.strip():
        st.session_state.chat.append(("user", user))

        if client:
            fixed = "\n\n".join(
                [f"Q: {q}\nA: {a}" for q, a in m["questions"]]
            )

            system = f"""
당신은 심방세동 환자 교육 챗봇입니다.

현재 교육 주제는 '{m['name']}'입니다.

아래 고정 교육내용과
대한부정맥학회 2024 심방세동 진료지침,
2024 ESC 심방세동 진료지침,
2023 ACC/AHA/ACCP/HRS 심방세동 진료지침 범위에서
환자가 이해하기 쉬운 한국어로 답변합니다.

개인의 진단을 하지 않습니다.
약물의 시작, 중단, 용량 변경을 지시하지 않습니다.
개인별 시술 여부를 결정하지 않습니다.
응급 증상이 의심되는 경우 119 또는 응급실 이용을 우선 안내합니다.

아주대학교병원 전화예약센터는 1688-6114,
응급실 안내는 031-219-7777입니다.

[현재 교육내용]

{fixed}
"""

            try:
                r = client.responses.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
                    input=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ]
                )
                ans = (r.output_text or "").strip()
                if not ans:
                    ans = "답변을 생성하지 못했습니다. 담당 의료진에게 문의해 주세요."
            except Exception:
                ans = (
                    "현재 추가 질문 답변을 불러오지 못했습니다. "
                    "고정 교육내용을 참고하거나 담당 의료진에게 문의해 주세요."
                )
        else:
            ans = "현재 OPENAI_API_KEY가 설정되지 않아 자유질문 AI 답변은 사용할 수 없습니다."

        st.session_state.chat.append(("assistant", ans))
        st.rerun()

    for role, text in st.session_state.chat[-8:]:
        with st.chat_message(role):
            st.markdown(text)

# =========================================================
# 병원 이용 안내
# =========================================================
st.markdown(
    """
    <div class='hospital'>
        <b>☎ 아주대학교병원 이용 안내</b><br>
        전화예약센터 <b>1688-6114</b>
        &nbsp; | &nbsp;
        응급실 안내 <b>031-219-7777</b><br>
        <small>
        갑작스러운 마비 또는 말 어눌함,
        심한 흉통이나 호흡곤란,
        실신 또는 의식변화,
        멈추지 않는 심한 출혈 등 응급상황이 의심되면
        챗봇 답변을 기다리지 말고 119 또는 가까운 응급실을 이용하세요.
        </small>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 교육 근거
# =========================================================
with st.expander("📚 교육내용 근거"):
    st.markdown(
        """
- 2024 대한부정맥학회 심방세동 일반 치료 진료지침
- 2024 대한부정맥학회 심방세동 시술적 치료 진료지침
- 2024 대한부정맥학회 심방세동 NOAC 치료 진료지침
- 2024 ESC Guidelines for the management of atrial fibrillation
- 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation
        """
    )
