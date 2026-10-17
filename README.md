# inventory-management-fastapi

A small inventory management system built with **FastAPI** and **SQLite**, exposing REST endpoints for managing users, products, and sales transactions. Stock levels are kept in sync automatically by SQLite triggers. A **Streamlit** front-end will be added later to link up the entire application.

## Features

- **User management** — create, list, update, and delete users. Each user is assigned a unique API token on creation.
- **Product management** — create, list, update, and delete products with stock tracking.
- **Sales transactions** — authenticated users can post sales; sales can be edited, and deleted by admins only.
- **Automatic stock control** — database triggers deduct, adjust, and restore stock on sale insert/update/delete, and reject sales that would make stock negative.
- **Token-based authentication** — sales endpoints require a Bearer token tied to a user; deleting a sale additionally requires admin privileges (`IsAdmin`).
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
├── main.py                # FastAPI entry point; registers the routers
├── database.py            # SQLite connection helper (row factory + foreign keys on)
├── dependencies.py        # Auth dependencies: get_current_user, require_admin
├── models/
│   ├── user.py            # Pydantic models for users
│   ├── product.py         # Pydantic models for products
│   └── sales.py           # Pydantic models for sales
├── routers/
│   ├── users.py           # User endpoints
│   ├── products.py        # Product endpoints
│   └── sales.py           # Sales endpoints
├── db_tiggers.sql         # SQLite triggers for stock management
├── inventorysystem.db     # SQLite database
└── README.md
```

## Database Schema

The app expects an `inventorysystem.db` SQLite database with the following tables:

- **users** — `Id` (PK), `name`, `ApiToken` (unique), `IsAdmin`
- **product** — `Id` (PK), `ProductCode`, `ProductName` (unique), `Stock`
- **sales** — `Id` (PK), `UserId` (FK → users.Id), `ProductId` (FK → product.Id), `Quantity`

Foreign keys are enforced via `PRAGMA foreign_keys = ON`.

### Database Triggers

Defined in [db_tiggers.sql](db_tiggers.sql) and applied to the database:

| Trigger | Fires | Effect |
|---------|-------|--------|
| `reduce_stock_after_sales` | AFTER INSERT on `sales` | Subtracts the sold quantity from the product's stock |
| `adjust_stock_after_sales_update` | AFTER UPDATE on `sales` | Restores the old quantity and deducts the new one (handles product changes too) |
| `adjust_stock_after_sales_delete` | AFTER DELETE on `sales` | Adds the deleted sale's quantity back to stock |
| `prevent_negative_stock_on_insert` | BEFORE INSERT on `sales` | Aborts with `Insufficient stock for this sale.` |
| `prevent_negative_stock_on_update` | BEFORE UPDATE on `sales` | Aborts with `Insufficient stock for this update.` |

Trigger errors surface through the API as `400` responses.

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
   pip install fastapi uvicorn pydantic
   ```

3. **Initialize the database** — create `inventorysystem.db` with the tables above, then run [db_tiggers.sql](db_tiggers.sql) against it to install the stock triggers.

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
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET    | `/sales`                    | None         | List all sales transactions |
| POST   | `/addsales`                 | Bearer token | Record a new sale for the authenticated user (by product name and quantity) |
| PUT    | `/editsales/{sales_id}`     | None         | Change a sale's product and/or quantity |
| DELETE | `/deletesales/{sales_id}`   | Admin token  | Delete a sale; stock is restored by trigger |

## Authentication

Protected endpoints (`/addsales`, `/deletesales/{sales_id}`) require an HTTP Bearer token:

```
Authorization: Bearer <ApiToken>
```

The token is generated and stored when a user is created via `/createuser`. An invalid token returns `401`. `/deletesales/{sales_id}` additionally requires the user's `IsAdmin` flag to be set, otherwise it returns `403`.

## Roadmap

- [ ] Add a **Streamlit** front-end to interact with the API.
- [ ] Add database migrations / init script (tables and triggers).
- [ ] Protect the remaining user, product, and sales-edit endpoints with authentication.
- [ ] Add reporting endpoints (e.g., sales per user, stock levels).
- [x] Stock deduction and negative-stock validation on sales (via triggers).
- [x] Split the app into routers, models, and dependencies.
