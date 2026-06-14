import os

class Settings:
    TABLE_NAME = os.environ.get("TABLE_NAME", "LifeGraph")
    REGION_NAME = os.environ.get("AWS_REGION", "ap-south-1")

settings = Settings()
