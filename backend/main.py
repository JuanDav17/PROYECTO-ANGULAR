# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import productos, usuarios, pedidos, ventas

app = FastAPI(title="API Gutkleid", version="2.0")

# Configuración CORS
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(pedidos.router)
app.include_router(ventas.router)

@app.get("/")
def root():
    return {
        "message": "API Gutkleid - Sistema de Roles",
        "version": "2.0",
        "endpoints": {
            "usuarios": "/usuarios",
            "productos": "/productos",
            "pedidos": "/pedidos",
            "ventas": "/ventas"
        }
    }