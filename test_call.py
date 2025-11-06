# test_call.py (리팩터링 후)
from law_api import search_old_and_new_list, fetch_old_and_new_detail

def main():
    results = search_old_and_new_list("화학물질관리법", display=5)
    print(results[0])

    mst = results[0]["MST"]
    detail = fetch_old_and_new_detail(mst)
    print(detail)

if __name__ == "__main__":
    main()
