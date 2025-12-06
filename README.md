
# Employee CRUD with FastAPI and Next.js

This project implements a basic employee CRUD using FastAPI with SQLite as the backend and Next.js as the frontend.

## Structure

- `backend/`: REST API built with FastAPI and SQLAlchemy.  
- `frontend/`: Next.js application that consumes the API to manage employees.  
- `docker-compose.yml`: Orchestration for running both services.

## Run with Docker

```bash
docker-compose up --build
````

* API available at `http://localhost:8000`
* Frontend available at `http://localhost:3000`

## Run Locally (optional)

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

The `NEXT_PUBLIC_API_URL` variable controls the API endpoint and defaults to `http://localhost:8000`.

---

## Architectural Note: Traditional CRUD vs CQRS

This project follows a **traditional CRUD architecture**, where **reads and writes are handled by the same models, database schema, handlers, and API routes**. This monolithic approach is simple and works for small systems, but introduces structural limitations:

### 1. No separation between Commands and Queries

CRUD couples:

* **State-changing operations** (create, update, delete)
* **Read-only operations** (list, get)

This single pipeline forces all operations to share the same data model and the same database workload, creating contention.

### 2. Scalability Limitations

Because reads and writes go through the same path:

* You cannot scale read-heavy and write-heavy workloads independently.
* Caching becomes harder since write operations invalidate the same model used for queries.
* Optimizing for analytical queries or projections forces changes in the core domain model.

### 3. Coupled Domain and Persistence Models

In CRUD:

* The API layer, domain logic, and database schema tend to mirror each other.
* Any schema change affects the whole stack.
* There is no space for **read-optimized models**, **denormalized views**, or **event-driven projections**.

### 4. CQRS Advantage (Conceptual Contrast)

CQRS (Command Query Responsibility Segregation) splits the system into two logical flows:

* **Commands**: mutate state, validated by domain rules.
* **Queries**: return data, optimized for reading, often through specialized view models.

This separation enables:

* Independent scaling of read/write workloads.
* Read models optimized for UX without affecting domain consistency.
* Use of asynchronous projections and event sourcing.
* Cleaner domain logic, enforcing invariants on the command side only.

---

This repository keeps the implementation intentionally simple—ideal for learning FastAPI + Next.js—but also illustrates why CRUD architecture becomes rigid as systems grow. Adding CQRS later would require splitting handlers, models, persistence flows, and creating independent read projections.

```
```
