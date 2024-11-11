
# FIDOTRANSACTIONMGMT API Service

## Table of Contents
- [FIDOTRANSACTIONMGMT API Service](#fidotransactionmgmt-api-service)
  - [Table of Contents](#table-of-contents)
    - [Overview](#overview)
    - [Features](#features)
    - [Project Structure](#project-structure)
    - [Setup and Run Instructions](#setup-and-run-instructions)
      - [Prerequisites](#prerequisites)
      - [Installation](#installation)
    - [Design and Architectural Decisions](#design-and-architectural-decisions)
    - [Scaling Strategies and Trade-offs](#scaling-strategies-and-trade-offs)
      - [1. **Database Sharding**](#1-database-sharding)
      - [2. **Task Queues**](#2-task-queues)
      - [3. **API Rate Limiting and Load Balancing**](#3-api-rate-limiting-and-load-balancing)
      - [4. **Monitoring and Alerting**](#4-monitoring-and-alerting)

---

### Overview

The **FIDOTRANSACTIONMGMT API Service** provides endpoints for managing and analyzing financial transactions for users. It includes functionality to authenticate users, retrieve analytics data, and process transactions efficiently through caching and background jobs.

### Features

- **User Authentication**: Handles user login and authentication with token-based security.
- **Analytics**: Provides transaction-based analytics for users, such as average transaction values and highest transaction days.
- **Transactions**: Allows users to add, view, and manage their transactions.
- **Caching with Redis**: Caches frequently requested analytics data for improved performance.
- **Asynchronous Background Jobs**: Uses asynchronous processing to handle analytics tasks without blocking user requests.

### Project Structure

The project structure is as follows:

```plaintext
app/
├── core/
│   ├── config.py              # Configuration for environment variables
│   └── security.py            # Security utilities (e.g., token handling)
│   ├── custom_exceptions/     
│       ├── exception_handlers.py # Custom exception handling
│       └── exceptions.py      # Custom exception definitions
├── db/
│   ├── models.py              # Database model definitions
│   └── session.py             # Database session setup
├── routers/
│   ├── analytics.py           # API route definitions for analytics
│   ├── auth.py                # Authentication route definitions
│   └── transactions.py        # Transaction management route definitions
├── schemas/
│   ├── auth.py                # Pydantic schemas for authentication
│   ├── transaction.py         # Pydantic schemas for transaction data
│   └── user.py                # Pydantic schemas for user data
├── services/
│   ├── analytics_service.py   # Analytics business logic
│   ├── auth_service.py        # Authentication-related logic
│   └── transaction_service.py # Transaction management logic
├── tests/
│   ├── test_analytics.py      # Unit tests for analytics endpoints
│   ├── test_transactions.py   # Unit tests for transaction endpoints
│   └── test_user_auth.py      # Unit tests for authentication endpoints
├── utils/
│   └── cache.py               # Utility functions for Redis caching
.env                           # Environment variable configuration
docker-compose.yml             # Docker Compose setup for services
Dockerfile                     # Dockerfile to build the app image
main.py                        # Entry point for FastAPI application
README.md                      # Project documentation
requirements.txt               # Python dependencies
```

### Setup and Run Instructions

To set up and run this project locally, follow these steps:

#### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Redis and PostgreSQL

#### Installation

1. **Clone the Repository**:
    ```bash
    git clone <repo_url>
    cd FIDOTRANSACTIONMGMT
    ```

2. **Environment Setup**:
   Create a `.env` file in the root directory with the following variables:

    ```env
    # Database configuration
      POSTGRES_USER=postgres
      POSTGRES_PASSWORD=NyXcE3RP2aSp
      POSTGRES_DB=fidoapi

      # # Redis configuration
      REDIS_PASSWORD=redis

      # Other configuration
      SECRET_KEY=791611d9d8a6d4624b1331494e3964ece2f9b80ff9b90ed22aef139cc58d03d4
      ACCESS_TOKEN_EXPIRE_MINUTES=30
      ALGORITHM=HS256
      ENCRYPTION_KEY=czs6ViNGbEVvP7qD-nE0V5HTZ9bY5xUqHbvNU3aLvoY=
    ```

3. **Run Docker Compose**:
    ```bash
    docker-compose --env-file .env up -d
    or
    docker compose --env-file .env up -d
    ```

4. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Run the Application**:
    ```bash
    uvicorn app.main:app --reload
    ```

6. **Access API Documentation**:
   Go to `http://localhost:8000/docs` for the Swagger UI or `http://localhost:8000/redoc`.

### Design and Architectural Decisions

- **Core Configuration**: Centralized configuration management (`config.py`) loads environment variables for easy modification and deployment.
- **Asynchronous Processing**: Async I/O and background jobs improve responsiveness, especially for analytics requests.
- **Redis Caching**: Used for frequently accessed analytics data to reduce database load and latency.
- **Custom Exceptions**: Custom exceptions ensure consistent error handling across endpoints.
- **Modular Services**: Divides business logic into services (e.g., `analytics_service.py`, `auth_service.py`) for maintainability and separation of concerns.

### Scaling Strategies and Trade-offs

#### 1. **Database Sharding**
   - **Strategy**: Shard the database by user segments or by type of transaction.
   - **Trade-off**: Complexity in analytics computations if data is distributed.

#### 2. **Task Queues**
   - **Strategy**: Use Celery or another task queue to manage background jobs at scale.
   - **Trade-off**: Queue management adds some delay to analytics processing.

#### 3. **API Rate Limiting and Load Balancing**
   - **Strategy**: Use a load balancer with rate limiting to manage traffic spikes.
   - **Trade-off**: Extra cost and configuration complexity, but necessary for high-traffic environments.

#### 4. **Monitoring and Alerting**
   - **Strategy**: Set up monitoring (e.g., Prometheus, Grafana) to identify bottlenecks and scale reactively.
   - **Trade-off**: Increases overhead but provides critical insights into application performance.

