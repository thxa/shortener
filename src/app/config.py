import os
class Settings:
    HOST_NAME = os.getenv("HOST_NAME", "127.0.0.1:8000")
    DB_CONFIG = {
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "fastapi"),
        "database": os.getenv("DB_NAME", "postgres"),
        "host": os.getenv("DB_HOST", "localhost"),
    }
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    RATE_LIMIT_TIMES = int(os.getenv("RATE_LIMIT_TIMES", 10))
    RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", 600))  # 10 minutes

settings = Settings()
