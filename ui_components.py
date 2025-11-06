import streamlit as st
import streamlit_shadcn_ui as ui

from utils import has_p_tag


def inject_global_css():
    """Global styles to ensure containers and dialogs behave properly."""
    st.markdown(
        """
<style>
/* Base font size */
html, body, [data-testid="stAppViewContainer"] { font-size: 14px; }

/* Main padding + max width to reduce overly wide layout */
main .block-container {
  padding-top: 1rem;
  padding-bottom: 2rem;
  max-width: 960px; /* reduce width further */
  margin: 0 auto;   /* center content */
}
/* Extra specificity to ensure width applies in wide layout */
[data-testid="stAppViewContainer"] main .block-container { max-width: 960px; margin: 0 auto; }

/* Dialog backdrop and layout */
[data-testid="stDialog"] {
    position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;
    background: rgba(15,23,42,0.35); z-index: 9999;
}
[data-testid="stDialog"] > div {
    width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
}
[data-testid="stDialog"] > div > div {
    width: 80vw !important; max-width: 80vw !important; max-height: 80vh !important;
    background: #ffffff; border-radius: 12px; padding: 1.5rem;
    /* Make content scroll within dialog to keep it contained */
    overflow: auto;
    box-shadow: 0 20px 40px rgba(15,23,42,0.35);
}

/* Article content typography */
.law-article { font-size: 0.9rem; line-height: 1.4; white-space: normal; word-break: keep-all; }
.law-article.old-article p, .law-article.new-article p { display: inline; margin: 0; padding: 0; }
.law-article.old-article p { color: #b91c1c; }
.law-article.new-article p { color: #2563eb; }
.law-article.old-article p + p::before, .law-article.new-article p + p::before { content: " "; }

/* Law card list and card styles */
.law-card-list { display: flex; flex-direction: column; gap: 0.5rem; }
.law-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #ffffff;
  padding: 10px 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
<<<<<<< ours
  position: relative;
  margin-bottom: 10px; /* ensure a bit of gap between cards */
  cursor: pointer;
=======
>>>>>>> theirs
}
.law-card:hover { box-shadow: 0 2px 6px rgba(0,0,0,0.06); }
.law-card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; margin-bottom: 6px; }
.law-card-title { font-weight: 700; font-size: 1rem; color: #111827; margin: 0; }
.law-card-badges { display: flex; flex-wrap: wrap; gap: 6px; margin: 0; }
.badge { display: inline-flex; align-items: center; height: 20px; padding: 0 8px; font-size: 12px; border-radius: 9999px; border: 1px solid; }
.badge-gray { background: #f9fafb; color: #374151; border-color: #e5e7eb; }
.badge-blue { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }
.badge-amber { background: #fffbeb; color: #b45309; border-color: #fde68a; }
.law-card-meta {
  display: grid; grid-template-columns: 1fr 1fr; gap: 4px 16px;
  font-size: 12px; color: #374151; margin-top: 6px;
}
.law-card-meta .label { color: #6b7280; margin-right: 4px; }
.law-card-footer { display: flex; justify-content: flex-end; }
.card-cta { margin-top: 4px; }
</style>
""",
        unsafe_allow_html=True,
    )


def render_filter_bar(start_date, end_date):
    """기간 필터 바: 컨테이너 안에 날짜와 버튼을 안전하게 배치."""
    with st.container(border=True):
        c1, c2, c3 = st.columns([1.2, 1.2, 0.8])

        with c1:
            start = st.date_input(
                "시작일 (변경일 기준)", value=start_date, format="YYYY-MM-DD", key="start_date_input"
            )
        with c2:
            end = st.date_input(
                "종료일 (변경일 기준)", value=end_date, format="YYYY-MM-DD", key="end_date_input"
            )
        with c3:
            st.write("")
            st.write("")
            search_btn = st.button("검색", use_container_width=True, key="search_btn")

    return search_btn, start, end


def render_law_cards(results):
    """변경된 법령 목록을 컴팩트 카드 형태로 표시(굵은 제목 + 배지 + 메타)."""
    st.subheader("변경된 법령 목록")

    if not results:
        st.info("검색 결과가 없습니다.")
        return

    st.markdown('<div class="law-card-list">', unsafe_allow_html=True)
    for idx, r in enumerate(results):
        law_name = r.get("법령명한글", "").strip()
        law_type = r.get("법령구분", "").strip() or r.get("법령구분명", "").strip()
        change_type = r.get("제개정구분명", "").strip() or r.get("제개정구분", "").strip()
        ministry = (
            r.get("소관부처명", "").strip()
            or r.get("소관부서명", "").strip()
            or r.get("주관부처명", "").strip()
        )

        promulgation_date = r.get("공포일자", "")
        enforcement_date = r.get("시행일자", "")
        promulgation_no = r.get("공포번호", "")
        reg_dt = r.get("변경일", "")

        # Build compact HTML card
        badges_html = " ".join([
            f'<span class="badge badge-gray">{law_type}</span>' if law_type else "",
            f'<span class="badge badge-blue">{change_type}</span>' if change_type else "",
            f'<span class="badge badge-amber">{ministry}</span>' if ministry else "",
        ])

        meta_cell = lambda label, value: (
            f'<div><span class="label">{label}</span><span>{value or "-"}</span></div>'
        )
        meta_html = (
            '<div class="law-card-meta">'
            + meta_cell("공포일자", promulgation_date)
            + meta_cell("시행일자", enforcement_date)
            + meta_cell("공포번호", promulgation_no)
            + meta_cell("변경일", reg_dt)
            + "</div>"
        )

        card_html = (
            '<div class="law-card">'
            '  <div class="law-card-head">'
            f'    <div class="law-card-title">{law_name}</div>'
            f'    <div class="law-card-badges">{badges_html}</div>'
            '  </div>'
            f"  {meta_html}"
<<<<<<< ours
            f'  <a class="card-overlay" href="?open={idx}" target="_self" role="button" aria-label="비교 열기"></a>'
            "</div>"
        )

        st.markdown(card_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
=======
            "</div>"
        )

        left, right = st.columns([12, 2])
        with left:
            st.markdown(card_html, unsafe_allow_html=True)
        with right:
            clicked = ui.button(
                text="비교",
                variant="secondary",
                class_name="card-cta",
                key=f"law_card_open_{idx}",
            )
            if clicked:
                st.session_state["modal_idx"] = idx
>>>>>>> theirs


def render_comparison_modal(selected, old_map, new_map):
    """개정 전/후 조문 비교 모달: 컨테이너 안에서 스크롤되도록 보장."""
    st.markdown(f"### {selected.get('법령명한글', '')}")

    st.write(
        f"{selected.get('법령구분', '')} · {selected.get('제개정구분명', '')} · {selected.get('소관부처명', '')}"
    )
    st.write(
        f"**공포일자**: {selected.get('공포일자', '')} / "
        f"**시행일자**: {selected.get('시행일자', '')} / "
        f"**공포번호**: {selected.get('공포번호', '')} / "
        f"**변경일(regDt)**: {selected.get('변경일', '')}"
    )
    st.write(f"**MST**: `{selected.get('MST', '')}`")

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
        st.info("변경된 조문(p 태그 포함)이 없습니다.")
        return

    st.markdown("#### 변경된 조문")
    st.divider()

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
