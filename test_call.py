# test_call.py
from ingestors.nlic_client import search_laws, get_law_body_by_id

def main():
    # 1) 검색어로 법령 목록 조회 (예: 화학물질관리법)
    res = search_laws({
        "search": 1,          # 검색 모드
        "query": "화학물질관리법",
        "display": 5,         # 5개만 가져와 보기
        "sort": "ddes",       # 공포일 내림차순
    })

    laws = res.get("law", [])
    print("검색 결과 수:", len(laws))
    for it in laws:
        print(it.get("법령ID"), it.get("법령명"))

    # 2) 첫 번째 검색 결과의 법령ID로 본문 조회
    if laws:
        first = laws[0]
        law_id = first.get("법령ID")
        print("\n=== 첫 번째 법령 본문 조회 ===")
        body = get_law_body_by_id(law_id)
        print("법령명:", body.get("법령명"))
        print("시행일자:", body.get("시행일자"))
        # 조문 목록 일부 확인 (키 이름은 실제 응답 보고 조정 필요)
        jo_list = body.get("조문") or body.get("조문목록") or []
        print("조문 개수:", len(jo_list))

if __name__ == "__main__":
    main()
