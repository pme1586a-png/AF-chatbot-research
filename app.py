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
# 화면 디자인
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
    .main-title {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        white-space: nowrap;
        font-size: clamp(1.15rem, 4vw, 2rem);
        font-weight: 750;
        line-height: 1.2;
        margin-bottom: 0.25rem;
    }

    .ecg-icon {
        font-size: 1.15em;
        flex-shrink: 0;
    }

    @media (max-width: 480px) {
        .main-title {
            font-size: 1.15rem;
        }
    }

    @media (max-width: 360px) {
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
# 제목
# =========================================================
st.markdown(
    """
    <div class="main-title">
        <span class="ecg-icon">〰️</span>
        <span>심방세동 AI 챗봇 교육</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "심방세동 환자를 위한 교육용 챗봇 · "
    "8개 교육 주제 + 추가 자유질문"
)


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
# 교육 주제 순서 고정
# =========================================================
MODULE_ORDER = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8"
]


# =========================================================
# OpenAI 연결
# =========================================================
def get_client():

    key = os.getenv(
        "OPENAI_API_KEY",
        ""
    ).strip()

    if key:
        return OpenAI(api_key=key)

    return None


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

    if st.button(
        "🏠 첫 화면으로",
        key="go_home",
        use_container_width=True
    ):

        go_home()
        st.rerun()


    st.header("교육 주제")


    for mid in MODULE_ORDER:

        m = MODULES[mid]

        if st.button(
            f"{m['icon']} {mid}. {m['name']}",
            key=f"sidebar_{mid}",
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

    st.caption(
        "응급상황은 119 또는 가까운 응급실을 우선 이용하세요."
    )


# =========================================================
# 첫 화면
# =========================================================
if st.session_state.module is None:

    st.subheader(
        "원하는 교육 주제를 선택하세요"
    )


    cols = st.columns(2)


    for idx, mid in enumerate(MODULE_ORDER):

        m = MODULES[mid]

        with cols[idx % 2]:

            if st.button(
                f"{m['icon']}  {mid}. {m['name']}",
                key=f"home_{mid}",
                use_container_width=True
            ):

                select_module(mid)
                st.rerun()


    st.info(
        "교육내용은 대한부정맥학회 2024 심방세동 진료지침, "
        "2024 ESC 및 2023 ACC/AHA/ACCP/HRS "
        "심방세동 진료지침을 중심으로 구성했습니다."
    )


    st.divider()


    st.subheader(
        "💬 추가로 궁금한 내용을 자유롭게 질문해 주세요"
    )

    st.caption(
        "개인 진단·처방·약물 용량 변경·"
        "개인별 시술 결정은 제공하지 않습니다."
    )


    client = get_client()


    q_col, send_col = st.columns(
        [0.84, 0.16],
        gap="small"
    )


    with q_col:

        user = st.text_input(
            "자유질문",
            placeholder="예: 심방세동은 왜 생기나요?",
            key="home_chat",
            label_visibility="collapsed"
        )


    with send_col:

        send = st.button(
            "질문하기",
            key="home_send",
            use_container_width=True
        )


    if send and user.strip():

        st.session_state.chat.append(
            ("user", user)
        )


        if client:

            fixed = "\n\n".join(
                [
                    f"[{MODULES[mid]['name']}]\n"
                    + "\n".join(
                        [
                            f"Q: {q}\nA: {a}"
                            for q, a
                            in MODULES[mid]["questions"]
                        ]
                    )
                    for mid in MODULE_ORDER
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

근거가 부족하거나 개인 상태 확인이 필요한 경우
담당 의료진에게 문의하도록 안내합니다.

응급 증상이 의심되는 경우
119 또는 응급실 이용을 우선 안내합니다.

아주대학교병원 전화예약센터는 1688-6114,
응급실 안내는 031-219-7777입니다.

[고정 교육내용]

{fixed}
"""


            try:

                response = client.responses.create(
                    model=os.getenv(
                        "OPENAI_MODEL",
                        "gpt-5-mini"
                    ),
                    input=[
                        {
                            "role": "system",
                            "content": system
                        },
                        {
                            "role": "user",
                            "content": user
                        }
                    ]
                )


                answer = (
                    response.output_text or ""
                ).strip()


                if not answer:

                    answer = (
                        "답변을 생성하지 못했습니다. "
                        "담당 의료진에게 문의해 주세요."
                    )


            except Exception:

                answer = (
                    "현재 추가 질문 답변을 불러오지 못했습니다. "
                    "교육내용을 참고하거나 담당 의료진에게 문의해 주세요."
                )


        else:

            answer = (
                "현재 자유질문 AI 답변을 사용할 수 없습니다. "
                "교육 주제의 고정 교육내용은 이용할 수 있습니다."
            )


        st.session_state.chat.append(
            ("assistant", answer)
        )

        st.rerun()


    for role, text in st.session_state.chat[-8:]:

        with st.chat_message(role):
            st.markdown(text)


# =========================================================
# 교육 주제 화면
# =========================================================
else:

    mid = st.session_state.module
    m = MODULES[mid]


    st.header(
        f"{m['icon']} {mid}. {m['name']}"
    )


    st.write(
        "궁금한 질문을 선택하면 "
        "오른쪽에 교육내용이 표시됩니다."
    )


    question_col, answer_col = st.columns(
        [0.42, 0.58],
        gap="large"
    )


    with question_col:

        st.subheader("📋 교육 질문")


        for i, (q, a) in enumerate(
            m["questions"]
        ):

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

            st.info(
                "왼쪽에서 궁금한 질문을 선택해 주세요."
            )


        else:

            i = st.session_state.question
            q, a = m["questions"][i]


            st.markdown(
                f"### {q}"
            )


            st.markdown(
                f"""
                <div class="education-answer">
                    {a}
                </div>
                """,
                unsafe_allow_html=True
            )


            st.markdown(
                f"""
                <div class="education-source">
                    근거: {m['source']}
                </div>
                """,
                unsafe_allow_html=True
            )


    st.divider()


    st.subheader(
        "💬 추가로 궁금한 내용을 자유롭게 질문해 주세요"
    )


    st.caption(
        "개인 진단·처방·약물 용량 변경·"
        "개인별 시술 결정은 제공하지 않습니다."
    )


    client = get_client()


    q_col, send_col = st.columns(
        [0.84, 0.16],
        gap="small"
    )


    with q_col:

        user = st.text_input(
            "자유질문",
            placeholder="예: 시술 후에도 항응고제를 계속 먹어야 하나요?",
            key=f"module_chat_{mid}_{st.session_state.question}",
            label_visibility="collapsed"
        )


    with send_col:

        send = st.button(
            "질문하기",
            key=f"module_send_{mid}_{st.session_state.question}",
            use_container_width=True
        )


    if send and user.strip():

        st.session_state.chat.append(
            ("user", user)
        )


        if client:

            fixed = "\n\n".join(
                [
                    f"Q: {q}\nA: {a}"
                    for q, a
                    in m["questions"]
                ]
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

응급 증상이 의심되면
119 또는 응급실 이용을 우선 안내합니다.

아주대학교병원 전화예약센터는 1688-6114,
응급실 안내는 031-219-7777입니다.

[현재 교육내용]

{fixed}
"""


            try:

                response = client.responses.create(
                    model=os.getenv(
                        "OPENAI_MODEL",
                        "gpt-5-mini"
                    ),
                    input=[
                        {
                            "role": "system",
                            "content": system
                        },
                        {
                            "role": "user",
                            "content": user
                        }
                    ]
                )


                answer = (
                    response.output_text or ""
                ).strip()


                if not answer:

                    answer = (
                        "답변을 생성하지 못했습니다. "
                        "담당 의료진에게 문의해 주세요."
                    )


            except Exception:

                answer = (
                    "현재 추가 질문 답변을 불러오지 못했습니다. "
                    "교육내용을 참고하거나 담당 의료진에게 문의해 주세요."
                )


        else:

            answer = (
                "현재 자유질문 AI 답변을 사용할 수 없습니다."
            )


        st.session_state.chat.append(
            ("assistant", answer)
        )

        st.rerun()


    for role, text in st.session_state.chat[-8:]:

        with st.chat_message(role):
            st.markdown(text)


# =========================================================
# 병원 이용 안내
# =========================================================
st.markdown(
    """
    <div class="hospital">

        <b>☎ 아주대학교병원 이용 안내</b><br>

        전화예약센터 <b>1688-6114</b>
        &nbsp; | &nbsp;
        응급실 안내 <b>031-219-7777</b>

        <br>

        <small>
        갑작스러운 마비 또는 말 어눌함,
        심한 흉통이나 호흡곤란,
        실신 또는 의식변화,
        멈추지 않는 심한 출혈 등
        응급상황이 의심되면
        챗봇 답변을 기다리지 말고
        119 또는 가까운 응급실을 이용하세요.
        </small>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 교육 근거
# =========================================================
with st.expander(
    "📚 교육내용 근거"
):

    st.markdown(
        """
- 2024 대한부정맥학회 심방세동 일반 치료 진료지침
- 2024 대한부정맥학회 심방세동 시술적 치료 진료지침
- 2024 대한부정맥학회 심방세동 NOAC 치료 진료지침
- 2024 ESC Guidelines for the management of atrial fibrillation
- 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation
        """
    )
