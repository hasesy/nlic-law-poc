import streamlit as st
import streamlit_shadcn_ui as ui
from utils import has_p_tag


def inject_global_css():
    """전역 스타일 정의"""
    st.markdown(
        """
<style>
html, body, [data-testid="stAppViewContainer"] {
    font-size: 14px;
}

/* 메인 여백 */
main .block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}

/* 상단 필터 박스 */
.filter-bar {
    padding: 0.75rem 1rem;
    border-radius: 12px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    margin-bottom: 0.75rem;
}

/* 모달 스타일 */
[data-testid="stDialog"] {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(15,23,42,0.35);
    z-index: 9999;
}
[data-testid="stDialog"] > div {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
[data-testid="stDialog"] > div > div {
    width: 80vw !important;
    max-width: 80vw !important;
    max-height: 80vh !important;
    background: #ffffff;
    border-radius: 12px;
    padding: 1.5rem;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(15,23,42,0.35);
}

/* 모달 안 스크롤 영역 */
.article-scroll {
    max-height: calc(80vh - 180px);
    overflow-y: auto;
    padding-right: 0.5rem;
}

/* 신·구 조문 영역 */
.law-article {
    font-size: 0.9rem;
    line-height: 1.4;
    white-space: normal;
    word-break: keep-all;
}
.law-article.old-article p,
.law-article.new-article p {
    display: inline;
    margin: 0;
    padding: 0;
}
.law-article.old-article p {
    color: #b91c1c;
}
.law-article.new-article p {
    color: #2563eb;
}
.law-article.old-article p + p::before,
.law-article.new-article p + p::before {
    content: " ";
}

/* 카드 간 여백 */
div[data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] {
    margin-bottom: 1rem;
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_filter_bar(start_date, end_date):
    """상단 기간 필터 바 (Streamlit 기본 카드 스타일)"""
    with st.container():
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1.2, 1.2, 0.8])

        with c1:
            start = st.date_input(
                "시작일 (변경일 기준)",
                value=start_date,
                format="YYYY-MM-DD",
                key="start_date_input",
            )
        with c2:
            end = st.date_input(
                "종료일 (변경일 기준)",
                value=end_date,
                format="YYYY-MM-DD",
                key="end_date_input",
            )
        with c3:
            st.write(" ")
            st.write(" ")
            search_btn = st.button("검색", use_container_width=True, key="search_btn")

        st.markdown("</div>", unsafe_allow_html=True)

    return search_btn, start, end


def render_law_cards(results):
    """변경된 법령 목록 카드 리스트 (shadcn-ui + badge 포함 버전)"""
    st.subheader("변경된 법령 목록")

    if not results:
        st.info("검색 결과가 없습니다.")
        return

    for idx, r in enumerate(results):
        with ui.card(key=f"law_card_{idx}"):
            # 제목
            st.markdown(f"### {r['법령명한글']}", unsafe_allow_html=True)

            # 뱃지 (법령 구분 / 제·개정 구분 / 소관부처)
            ui.badges(
                badge_list=[
                    (r["법령구분명"], "outline"),
                    (r["제개정구분명"], "secondary"),
                    (r["소관부처명"], "default"),
                ],
                class_name="mt-2",
                key=f"law_badges_{idx}",
            )

            # 날짜/공포번호
            st.markdown(
                f"""
                <div style='font-size: 0.85rem; color: #64748b; margin-top: 0.35rem;'>
                  공포일자: {r['공포일자']} / 시행일자: {r['시행일자']}<br>
                  공포번호: {r['공포번호']} / 변경일: {r['변경일']}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 버튼
            clicked = ui.button(
                text="신·구조문 비교 보기",
                key=f"law_card_btn_{idx}",
                variant="outline",
            )

            if clicked:
                st.session_state["modal_idx"] = idx


def render_comparison_modal(selected, old_map, new_map):
    """신구법 비교 모달 내용"""
    st.markdown(f"### {selected['법령명한글']}")

    st.write(
        f"{selected['법령구분명']} · {selected['제개정구분명']} · {selected['소관부처명']}"
    )
    st.write(
        f"**공포일자**: {selected['공포일자']} / "
        f"**시행일자**: {selected['시행일자']} / "
        f"**공포번호**: {selected['공포번호']} / "
        f"**변경일(regDt)**: {selected['변경일']}"
    )
    st.write(f"**MST**: `{selected['MST']}`")

    article_nos = sorted(set(old_map.keys()) | set(new_map.keys()), key=lambda x: str(x))
    old_blocks, new_blocks = [], []

    for no in article_nos:
        old_text = old_map.get(no, "")
        new_text = new_map.get(no, "")

        if not (has_p_tag(old_text) or has_p_tag(new_text)):
            continue

        if old_text:
            old_blocks.append(f"<div><strong>[{no}]</strong> {old_text}</div>")
        if new_text:
            new_blocks.append(f"<div><strong>[{no}]</strong> {new_text}</div>")

    if not old_blocks and not new_blocks:
        st.info("변경된 부분(<p> 태그가 포함된 조문)을 찾지 못했습니다.")
        return

    st.markdown("#### 🔀 변경된 조문")
    st.markdown('<div class="article-scroll">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**개정 전**")
        st.markdown(
            f'<div class="law-article old-article">{"".join(old_blocks)}</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown("**개정 후**")
        st.markdown(
            f'<div class="law-article new-article">{"".join(new_blocks)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
