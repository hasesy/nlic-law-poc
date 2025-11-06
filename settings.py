# settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 국가법령정보센터 DRF(Open API) 기본 URL
    NLIC_BASE: str = "http://www.law.go.kr/DRF"

    # 여기 **본인 계정 이메일의 @ 앞부분**으로 바꿔야 함
    # 예) 이메일이 aaa@bbb.com 이면 NLIC_OC = "aaa"
    NLIC_OC: str = "your_oc"

    REQUEST_TIMEOUT: int = 30
    PAGE_SIZE: int = 100
    FETCH_WINDOW_HOURS: int = 3

    # 아직 DB 안 쓸 거라 일단 형식만 맞춰둠 (나중에 Postgres 연결할 때 수정)
    PG_DSN: str = "dbname=shms user=postgres host=localhost password=postgres"

    USER_AGENT: str = "Andami-SHMS/1.0"

settings = Settings()
