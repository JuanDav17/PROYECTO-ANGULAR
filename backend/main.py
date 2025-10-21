# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- NUEVA IMPORTACIÓN
from routers import productos, usuarios

app = FastAPI(title="API Gutkleid", version="1.0")

# 1. DEFINICIÓN DE ORÍGENES PERMITIDOS
origins = [
    "http://localhost:4200",  # El origen de tu aplicación Angular
    "http://127.0.0.1:4200",
]

# 2. AGREGAR EL MIDDLEWARE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Permite la comunicación desde tu frontend
    allow_credentials=True,     # Permite cookies/tokens
    allow_methods=["*"],        # Permite todos los métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],        # Permite todos los encabezados
)

# Agregamos los routers
app.include_router(productos.router)
app.include_router(usuarios.router)

@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}
