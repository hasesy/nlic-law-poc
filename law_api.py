from __future__ import annotations

import difflib
from datetime import date, timedelta
from urllib.parse import urlparse, parse_qs

import requests

from settings import settings


# =========================
# 기본 설정 (settings.py 사용)
# =========================
NLIC_BASE = settings.NLIC_BASE       # 예: http://www.law.go.kr/DRF
OC = settings.NLIC_OC                # .env 에서 가져온 OC
REQUEST_TIMEOUT = settings.REQUEST_TIMEOUT

SEARCH_URL = f"{NLIC_BASE}/lawSearch.do"
DETAIL_URL = f"{NLIC_BASE}/lawService.do"


def _to_yyyymmdd(d: date | str) -> str:
    if isinstance(d, date):
        return d.strftime("%Y%m%d")
    s = str(d).strip()
    if "-" in s and len(s) == 10:
        return s.replace("-", "")
    return s


def _parse_date_to_date(d: date | str) -> date:
    if isinstance(d, date):
        return d
    s = str(d).strip()
    if "-" in s:
        y, m, d2 = s.split("-")
    else:
        y, m, d2 = s[:4], s[4:6], s[6:8]
    return date(int(y), int(m), int(d2))


def extract_mst_from_law_link(link: str | None) -> str | None:
    """
    lsHstInf의 '법령상세링크'에서 MST 추출
    예: /DRF/lawService.do?OC=sykim&target=law&MST=279191&type=HTML&...
    """
    if not link:
        return None
    try:
        # 절대 URL이 아니니 임시 도메인 붙여서 파싱
        if link.startswith("/"):
            link = "http://www.law.go.kr" + link
        parsed = urlparse(link)
        qs = parse_qs(parsed.query)
        return qs.get("MST", [None])[0]
    except Exception:
        return None


# ========= 1) 하루 기준 법령 변경이력 목록 (lsHstInf) =========
def search_change_history_by_date(
    reg_date: date | str,
    display: int = 100,
    page: int = 1,
):
    """
    법령 변경이력 목록 조회 (target=lsHstInf)
    :param reg_date: 변경일 (YYYYMMDD or date)
    """
    reg_str = _to_yyyymmdd(reg_date)

    params = {
        "OC": OC,
        "target": "lsHstInf",
        "type": "JSON",
        "regDt": reg_str,
        "display": display,
        "page": page,
    }

    print("[lsHstInf] 요청 파라미터:", params)

    resp = requests.get(SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
    print("[lsHstInf] status:", resp.status_code)
    print("[lsHstInf] raw response 앞 500자:", resp.text[:500])

    resp.raise_for_status()
    data = resp.json()
    print("[lsHstInf] parsed JSON keys:", list(data.keys()))

    root = data.get("LawSearch", {})
    items = root.get("law", [])

    if isinstance(items, dict):
        items = [items]

    results = []
    for item in items:
        상세링크 = item.get("법령상세링크")
        mst = extract_mst_from_law_link(상세링크)

        results.append({
            "법령일련번호": item.get("법령일련번호"),
            "법령명한글": item.get("법령명한글"),
            "법령ID": item.get("법령ID"),
            "공포일자": item.get("공포일자"),
            "공포번호": item.get("공포번호"),
            "제개정구분명": item.get("제개정구분명"),
            "소관부처명": item.get("소관부처명"),
            "법령구분명": item.get("법령구분명"),
            "시행일자": item.get("시행일자"),
            "자법타법여부": item.get("자법타법여부"),
            "법령상세링크": 상세링크,
            "MST": mst,          # oldAndNew에 바로 쓸 수 있는 후보
            "변경일": reg_str,
        })
    return results


def search_change_history_by_period(
    start_date: date | str,
    end_date: date | str,
):
    """
    기간 동안의 법령 변경이력 통합 조회 (여러 regDt를 합침)
    """
    start = _parse_date_to_date(start_date)
    end = _parse_date_to_date(end_date)

    all_results = []
    seen = set()  # (법령ID, 공포일자, 공포번호) 로 중복 제거

    cur = start
    while cur <= end:
        day_results = search_change_history_by_date(cur, display=100, page=1)
        for r in day_results:
            key = (r["법령ID"], r["공포일자"], r["공포번호"])
            if key not in seen:
                seen.add(key)
                all_results.append(r)
        cur += timedelta(days=1)

    print("[lsHstInf] 기간 통합 결과 건수:", len(all_results))
    return all_results


def fetch_old_and_new_detail(mst: str):
    """
    신구법 본문 조회 API (oldAndNew) – MST 기준
    """
    params = {
        "OC": OC,
        "target": "oldAndNew",
        "type": "JSON",
        "MST": mst,
    }
    print("[oldAndNew] 요청 파라미터:", params)

    resp = requests.get(DETAIL_URL, params=params, timeout=REQUEST_TIMEOUT)
    print("[oldAndNew] status:", resp.status_code)
    print("[oldAndNew] raw response 앞 500자:", resp.text[:500])

    resp.raise_for_status()
    data = resp.json()
    print("[oldAndNew] parsed JSON keys:", list(data.keys()))
    return data


def extract_articles_from_old_and_new(data: dict):
    """
    신구법 JSON 응답에서 구조문/신조문 '조문 목록'을 파싱해서
    {번호: 내용} 형태의 dict 두 개를 반환

    - 루트 키: OldAndNewService 또는 oldAndNew
    - 구조문목록 / 신조문목록 내부 구조:
        {"조문": [ { "content": "...", "no": "1" }, ... ] }
      또는
        [ { "조문번호": "...", "조문내용": "..." }, ... ]
    """
    # 루트 키 처리: OldAndNewService 우선, 그다음 oldAndNew, 없으면 data 자체
    root = data.get("OldAndNewService") or data.get("oldAndNew") or data

    def parse_block(block):
        if not block:
            return {}

        # {"조문": [...]} 형태면 안쪽 리스트 꺼내기
        if isinstance(block, dict) and "조문" in block:
            articles = block["조문"]
        else:
            articles = block

        # 조문이 dict 하나로 올 수도 있음
        if isinstance(articles, dict):
            articles = [articles]

        result: dict[str, str] = {}
        for a in articles or []:
            # 번호 후보들
            no = (
                a.get("조문번호")
                or a.get("조문ID")
                or a.get("조")
                or a.get("no")            # OldAndNewService 샘플
            )
            # 내용 후보들
            text = (
                a.get("조문내용")
                or a.get("조문")
                or a.get("content")       # OldAndNewService 샘플
                or ""
            )
            if no:
                result[str(no)] = str(text)

        return result

    # 구조문(구법) / 신조문(신법) 각각 파싱
    old_block = root.get("구조문목록")
    new_block = root.get("신조문목록")

    old_map = parse_block(old_block)
    new_map = parse_block(new_block)

    print("[oldAndNew] parsed articles - old_map keys:", list(old_map.keys()))
    print("[oldAndNew] parsed articles - new_map keys:", list(new_map.keys()))

    return old_map, new_map


def make_article_diff(old_text: str, new_text: str) -> str:
    """
    두 조문 텍스트를 줄 단위로 비교해서 unified diff 문자열 생성.
    Streamlit에서 st.code(diff, language="diff")로 출력 가능.
    """
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile="구조문",
        tofile="신조문",
        lineterm=""
    )
    return "\n".join(diff)
