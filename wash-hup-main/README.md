# Wash-Hup API

This repository contains the backend API for "Wash-Hup," an on-demand car washing application designed to connect car owners with mobile car wash service providers.

## Core Technologies

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** [PostgreSQL](https://www.postgresql.org/)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Caching & Geolocation:** [Redis](https://redis.io/)
- **Real-time Communication:** [WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- **Geolocation Toolkit:** [GeoAlchemy2](https://geoalchemy-2.readthedocs.io/)
- **Dependency Management:** [pip](https://pip.pypa.io/en/stable/)

## Architecture Overview

The Wash-Hup API is built using a modern Python stack, emphasizing performance and clean design.

- **High-Performance API:** Built on **FastAPI** with ASGI, the API is asynchronous from the ground up, ensuring high throughput for I/O-bound operations.
- **Structured by Role:** The API endpoints are logically organized by user roles (`/client`, `/washer`, `/admin`) and common functionalities (`/auth`, `/user`), promoting separation of concerns and maintainability.
- **Relational Data Store:** **PostgreSQL** serves as the primary database, managed by the powerful **SQLAlchemy** ORM. Database schema changes are handled systematically using **Alembic** migrations.
- **Real-time Geospatial Features:** **Redis** is leveraged not just for caching but also for its powerful geospatial indexing capabilities. This allows the system to efficiently find the nearest available washers for a client's request.
- **Instantaneous Communication:** **WebSockets** facilitate a real-time, bidirectional communication channel between the server and clients. This is critical for features like sending immediate wash offers to washers and providing live status updates.
- **Authentication:** Secure authentication is implemented using **JSON Web Tokens (JWT)**, ensuring that API endpoints are accessed safely.

## Key Features

- **User Authentication:** Secure user registration and login for clients and washers.
- **Profile Management:** Users can manage their profiles, including vehicle information for clients and service details for washers.
- **On-Demand Booking:** Clients can book a car wash at their current location.
- **Geospatial Matching:** The system automatically finds and notifies the closest available washers.
- **Real-time Offer System:** Washers receive booking offers in real-time and can accept or decline them.
- **Support System:** A built-in issue tracking system for users to report problems.
- **Admin Interface:** Full administrative dashboard for managing users, verification, prices, and orders.

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd WashHup
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    -   Copy the example environment file:
        ```bash
        # On Windows
        copy .env.example .env
        # On macOS/Linux
        cp .env.example .env
        ```
    -   Edit the `.env` file and provide the necessary credentials:
        *   `SQLALCHEMY_DATABASE_URL`: Your PostgreSQL connection string (e.g., `postgresql://user:password@localhost/dbname`).
        *   `REDIS_HOST`, `REDIS_PORT`: Your Redis server details.
        *   `SECRET_KEY`: For JWT token signing.
        *   `RESEND_API_KEY`: For sending emails.

5.  **Run database migrations:**
    -   Make sure your PostgreSQL server is running.
    -   Apply the migrations to create the database schema:
        ```bash
        alembic upgrade head
        ```

6.  **Run the application:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

## Admin Modules Structure

The administrative functionalities are fully implemented and organized within the `app/api/endpoints/admin/` directory:

```text
wash-hup-main/app/
├── api/
│   └── endpoints/
│       └── admin/
│           ├── accounts.py      # User management, verification, and status control.
│           ├── dashboard.py     # Statistics, revenue tracking, and trend charts.
│           ├── orders.py        # Order management and service price regulation.
│           ├── issues.py        # REST endpoints for support issue management.
│           ├── emails.py        # Administrative email and broadcast tools.
│           ├── auth.py          # Admin authentication.
│           ├── wallet.py        # Financial and remission management.
│           └── index.py         # Main Admin Router registration.
├── websocket/
│   └── handlers/
│       └── issue_admin.py       # Real-time admin issue handling.
└── utils/
    └── email.py                 # Core email utility functions.
```

## API Structure

The API endpoints are organized into logical groups:

-   `/auth`: Handles user creation, login, and token management.
-   `/api/v1/client`: Endpoints for client-specific actions (e.g., booking a wash).
-   `/api/v1/washer`: Endpoints for washer-specific actions (e.g., managing profile, accepting offers).
-   `/api/v1/user`: Endpoints for general user actions (e.g., profile updates, support issues).
-   `/api/v1/admin`: Comprehensive administrative management endpoints.
-   `/ws`: WebSocket endpoint for real-time bidirectional communication.
