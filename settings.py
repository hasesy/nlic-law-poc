# settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 국가법령정보센터 DRF(Open API) 기본 URL
    NLIC_BASE: str = "http://www.law.go.kr/DRF"

    # OpenAPI 사용자 인증키 (이메일 @ 앞부분)
    NLIC_OC: str  # ← 기본값 제거 (환경변수에서 반드시 읽도록)

    REQUEST_TIMEOUT: int = 30
    PAGE_SIZE: int = 100
    FETCH_WINDOW_HOURS: int = 3

    PG_DSN: str = "dbname=shms user=postgres host=localhost password=postgres"
    USER_AGENT: str = "Andami-SHMS/1.0"

    # .env 자동 로드 설정
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# settings 인스턴스 생성
settings = Settings()
