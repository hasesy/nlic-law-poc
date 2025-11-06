# ingestors/nlic_client.py
import time
import requests
from typing import Dict, Any
from settings import settings

# 공통 헤더 (User-Agent는 예의상/운영상 꼭 넣어주는 게 좋음)
H = {"User-Agent": settings.USER_AGENT}

def _get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    NLIC_BASE + path 에 GET 요청 보내고 JSON으로 반환.
    5번까지 지수 백오프(1,2,4,8,16초)로 재시도.
    """
    url = f"{settings.NLIC_BASE}/{path}"
    for i in range(5):
        try:
            r = requests.get(url, params=params, headers=H, timeout=settings.REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"[WARN] 요청 실패 {i+1}/5회: {e}")
            if i == 4:
                raise
            time.sleep(2 ** i)

def search_laws(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    lawSearch.do: 법령 목록 조회
    예) 검색어, 공포일, 시행일, 부처, 종류 등
    """
    base = {
        "OC": settings.NLIC_OC,
        "target": "law",
        "type": "JSON",
    }
    return _get("lawSearch.do", {**base, **params})

def get_law_body_by_id(law_id: str) -> Dict[str, Any]:
    """
    lawService.do: 특정 법령 ID 기준 본문 조회 (eflaw)
    """
    params = {
        "OC": settings.NLIC_OC,
        "target": "eflaw",
        "type": "JSON",
        "ID": law_id,
    }
    return _get("lawService.do", params)
