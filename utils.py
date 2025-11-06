def is_trivial_change(old_html: str, new_html: str) -> bool:
    """
    (이전 버전 호환용) 개정전이 (생 략)/(생략) 이고
    개정 후가 (현행과 같음)인 경우는 변경으로 보지 않는 로직.

    현재 화면에서는 사용하지 않고, has_p_tag() 기준으로 변경 여부를 판정한다.
    """
    if not old_html or not new_html:
        return False

    def normalize(s: str) -> str:
        # 공백/개행 전부 제거
        return "".join(str(s).split())

    old = normalize(old_html)
    new = normalize(new_html)

    cond_old_omit = "생략" in old      # "(생 략)" 도 normalize 후 "생략"에 걸림
    cond_new_same = "현행과같음" in new

    return cond_old_omit and cond_new_same


def has_p_tag(html: str) -> bool:
    """
    조문 HTML 안에 <p> 태그가 있는지 여부만으로
    '변경된 조문' 인지를 판별한다.
    """
    if not html:
        return False

    s = str(html).lower()
    return "<p" in s and "</p>" in s
