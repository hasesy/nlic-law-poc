from datetime import date, timedelta
import streamlit as st

from law_api import (
    search_change_history_by_period,
    fetch_old_and_new_detail,
    extract_articles_from_old_and_new,
)
from ui_components import (
    inject_global_css,
    render_filter_bar,
    render_law_cards,
    render_comparison_modal,
)

# =========================
# 페이지 기본 설정
# =========================
st.set_page_config(
    page_title="법령 변경 이력목록",
    layout="wide",
)
inject_global_css()

# =========================
# 세션 상태
# =========================
if "search_results" not in st.session_state:
    st.session_state["search_results"] = []
if "modal_idx" not in st.session_state:
    st.session_state["modal_idx"] = None
if "period" not in st.session_state:
    today = date.today()
    st.session_state["period"] = (today - timedelta(days=7), today - timedelta(days=7))

# =========================
# 헤더
# =========================
st.title("법령 변경 이력목록")

# =========================
# 필터 바 (Streamlit 기본 카드 스타일)
# =========================
period_start, period_end = st.session_state["period"]
search_btn, start_date, end_date = render_filter_bar(period_start, period_end)

# =========================
# 검색 실행
# =========================
if search_btn:
    if start_date > end_date:
        st.error("시작일이 종료일보다 늦을 수 없습니다.")
        st.session_state["search_results"] = []
    else:
        with st.spinner("법령 변경이력 목록 조회 중..."):
            try:
                results = search_change_history_by_period(start_date, end_date)
                st.session_state["search_results"] = results
                st.session_state["modal_idx"] = None
                st.session_state["period"] = (start_date, end_date)
            except Exception as e:
                st.error(f"법령 변경이력 목록 조회 실패: {e}")
                st.session_state["search_results"] = []

results = st.session_state["search_results"]

# =========================
# 카드 리스트 (shadcn-ui 기반)
# =========================
render_law_cards(results)

# =========================
# 모달: 선택한 법령 신·구 비교
# =========================
modal_idx = st.session_state.get("modal_idx")
if modal_idx is not None and 0 <= modal_idx < len(results):

    selected = results[modal_idx]

    @st.dialog("신구법 비교")
    def show_comparison_dialog():
        mst = selected.get("MST")
        if not mst:
            st.error("선택한 항목에 MST 정보가 없습니다.")
            if st.button("닫기"):
                st.session_state["modal_idx"] = None
            return

        with st.spinner("신구법 본문 조회 중... (oldAndNew)"):
            try:
                detail_json = fetch_old_and_new_detail(mst)
            except Exception as e:
                st.error(f"신구법 본문 조회 실패: {e}")
                if st.button("닫기"):
                    st.session_state["modal_idx"] = None
                return

        if detail_json:
            old_map, new_map = extract_articles_from_old_and_new(detail_json)
            if not old_map and not new_map:
                st.warning("구조문목록/신조문목록에서 조문을 찾지 못했습니다.")
            else:
                render_comparison_modal(selected, old_map, new_map)

        if st.button("닫기"):
            st.session_state["modal_idx"] = None

    show_comparison_dialog()
