# inventory-management-fastapi

A small inventory management system built with **FastAPI** and **SQLite**, exposing REST endpoints for managing users, products, and sales transactions. A **Streamlit** front-end will be added later to link up the entire application.

## Features

- **User management** — create, list, update, and delete users. Each user is assigned a unique API token on creation.
- **Product management** — create, list, update, and delete products with stock tracking.
- **Sales transactions** — authenticated users can post sales against existing products.
- **Token-based authentication** — sales endpoints and `/whoami` require a Bearer token tied to a user.
- **Pydantic validation** — input models validate and normalize data (e.g., title-casing names and product names).
- **SQLite backend** with foreign-key enforcement enabled.

## Tech Stack

- Python
- FastAPI
- Pydantic v2
- SQLite (`sqlite3`)
- Uvicorn (to run the app)
- Streamlit *(planned front-end)*

## Project Structure

```
.
├── main.py                # FastAPI application (users, products, sales endpoints)
├── inventorysystem.db     # SQLite database
└── README.md
```

## Database Schema

The app expects an `inventorysystem.db` SQLite database with the following tables:

- **users** — `Id` (PK), `name`, `ApiToken` (unique)
- **product** — `Id` (PK), `ProductCode`, `ProductName` (unique), `Stock`
- **sales** — `Id` (PK), `UserId` (FK → users.Id), `ProductId` (FK → product.Id), `Quantity`

Foreign keys are enforced via `PRAGMA foreign_keys = ON`.

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd inventory-management-fastapi
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   pip install fastapi uvicorn pydantic pandas
   ```

3. **Initialize the database** (create `inventorysystem.db` with the required tables).

4. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

5. Open the interactive API docs at `http://127.0.0.1:8000/docs`.

## API Endpoints

### General
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`      | Welcome message |
| GET    | `/whoami` | Returns the currently authenticated user (requires Bearer token) |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/user`              | List all users |
| POST   | `/createuser`        | Create a new user (auto-generates API token) |
| PUT    | `/edit/{Id}`         | Update an existing user |
| DELETE | `/delete/{user_id}`  | Delete a user by ID |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/product`                      | List all products |
| POST   | `/createproduct`                | Add a new product |
| PUT    | `/editproduct/{product_id}`     | Update a product's name or stock |
| DELETE | `/deleteproduct/{product_id}`   | Delete a product by ID |

### Sales
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/sales`     | List all sales transactions |
| POST   | `/addsales`  | Record a new sale (requires Bearer token) |

## Authentication

Protected endpoints (`/whoami`, `/addsales`) require an HTTP Bearer token:

```
Authorization: Bearer <ApiToken>
```

The token is generated and stored when a user is created via `/createuser`.

## Roadmap

- [ ] Add a **Streamlit** front-end to interact with the API.
- [ ] Add database migrations / init script.
- [ ] Add validation for stock deduction on sales.
- [ ] Add reporting endpoints (e.g., sales per user, stock levels).