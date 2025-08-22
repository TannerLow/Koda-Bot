from pydantic import BaseModel

class DatabaseSettings(BaseModel):
    save_filename: str
    save_folder: str
    