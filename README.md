# Employee CRUD with FastAPI and Next.js

Este proyecto implementa un CRUD básico de empleados usando FastAPI con SQLite como backend y Next.js como frontend.

## Estructura

- `backend/`: API REST construida con FastAPI y SQLAlchemy.
- `frontend/`: Aplicación Next.js que consume la API para gestionar empleados.
- `docker-compose.yml`: Orquestación para ejecutar ambos servicios.

## Ejecutar con Docker

```bash
docker-compose up --build
```

- API disponible en `http://localhost:8000`
- Frontend disponible en `http://localhost:3000`

## Ejecutar localmente (opcional)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

La variable `NEXT_PUBLIC_API_URL` controla la URL de la API y por defecto apunta a `http://localhost:8000`.
