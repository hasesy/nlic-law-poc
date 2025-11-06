# app/main.py
from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ingestors.nlic_client import search_laws

app = FastAPI()

# /static 경로에 정적 파일 제공 (index.html 넣을 예정)
app.mount("/static", StaticFiles(directory="static"), name="static")


def _search_laws_simple(q: str, limit: int = 20):
    """NLIC 응답을 화면에서 쓰기 쉬운 형태로 변환."""
    raw = search_laws({
        "search": 1,
        "query": q,
        "display": limit,
        "sort": "ddes",
    })

    wrapper = raw.get("LawSearch", {}) or {}
    laws = wrapper.get("law", []) or []

    items = []
    for it in laws:
        items.append({
            "seq": it.get("법령일련번호"),                  # 내부적으로 쓸 ID
            "title": it.get("법령명한글") or it.get("법령명"),
            "type": it.get("법령구분명"),
            "org": it.get("소관부처명"),
            "enforce_date": it.get("시행일자"),
            "link": it.get("법령상세링크"),
        })
    return items


@app.get("/api/search", summary="법령 검색 API")
def api_search(q: str = Query(..., description="법령명/키워드"), limit: int = 20):
    items = _search_laws_simple(q, limit)
    return {"items": items}


@app.get("/", response_class=HTMLResponse)
def root():
    # 간단히 static/index.html을 그대로 읽어서 반환
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

# 임시로 메모리 스텁 데이터 (나중에 DB/diff 붙이면 여기 구현만 바꾸면 됨)
_fake_changes = [
    {
        "law_id": "1747",
        "title": "화학물질관리법",
        "v_from": "20230101",
        "v_to": "20250101",
        "summary": "제10조 제2항 신설, 제15조 용어 정비"
    },
    {
        "law_id": "14532",
        "title": "화학물질관리법 시행령",
        "v_from": "20220101",
        "v_to": "20240101",
        "summary": "적용범위 확대, 보고 의무 강화"
    },
]

@app.get("/api/changes", summary="최근 변경된 법령 목록")
def api_changes(since_days: int = Query(30, ge=1, le=365)):
    # 지금은 그냥 스텁 데이터 그대로 반환 (since_days는 나중에 DB 기반에서 필터링에 사용)
    return {"items": _fake_changes}


@app.get("/api/laws/{law_id}/diff/latest", summary="특정 법령 최신 버전 Diff")
def api_law_latest_diff(law_id: str):
    # 간단 스텁: 위 목록에서 해당 law_id 찾아서, 변경 조문 예시 반환
    base = next((x for x in _fake_changes if x["law_id"] == law_id), None)
    if not base:
        return {"law_id": law_id, "v_from": None, "v_to": None, "changes": []}

    changes = [
        {
            "article": "제10조",
            "paragraph": "제2항",
            "change_type": "added",
            "before": None,
            "after": "사업자는 유해화학물질 취급시설에 대하여 정기적으로 안전점검을 실시하여야 한다."
        },
        {
            "article": "제15조",
            "paragraph": "제1항",
            "change_type": "modified",
            "before": "관계 법령에 따라 보고할 수 있다.",
            "after": "관계 법령에 따라 보고하여야 한다."
        }
    ]
    return {
        "law_id": law_id,
        "v_from": base["v_from"],
        "v_to": base["v_to"],
        "changes": changes,
    }