from pydantic import BaseModel

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    password: str

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str