from pydantic_settings import BaseSettings  # not in pydantic anymore in newer versions


class Settings(BaseSettings):  # environment variables
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:  # import things from the .env file where the variables are 
        env_file = ".env"


settings = Settings()