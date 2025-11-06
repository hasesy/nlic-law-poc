from ingestors.nlic_client import search_laws, get_law_body_by_id

def main():
    res = search_laws({
        "search": 1,
        "query": "화학물질관리법",
        "display": 5,
        "sort": "ddes",
    })

    # ★ 응답 구조: {"LawSearch": {"law": [ ... ]}}
    wrapper = res.get("LawSearch", {}) or {}
    laws = wrapper.get("law", []) or []

    print("검색 결과 수:", len(laws))
    for it in laws:
        print(it.get("법령일련번호"), it.get("법령명한글"))

    if laws:
        first = laws[0]
        # law_id는 응답 구조 보고 맞는 필드 쓰면 됨 (법령ID/법령일련번호 등)
        law_id = first.get("법령일련번호")
        print("\n=== 첫 번째 법령 본문 조회 ===")
        body = get_law_body_by_id(law_id)
        print("법령명:", body.get("법령명") or body.get("법령명한글"))
        print("시행일자:", body.get("시행일자"))
        jo_list = body.get("조문") or body.get("조문목록") or []
        print("조문 개수:", len(jo_list))

if __name__ == "__main__":
    main()
