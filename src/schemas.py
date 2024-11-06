from pydantic import BaseModel


# ===== todo schema =====

class TodoSchema(BaseModel):
    title : str
    description : str


# ===== jwt schemas =====

class LoginSchema(BaseModel):
    email : str
    password : str


class RefreshSchema(BaseModel):
    access_token : str
    token_type : str = 'bearer'