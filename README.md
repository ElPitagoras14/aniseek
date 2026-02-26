# Anime Scraper Monorepo

## Table of Contents

*   [Description](#description)
*   [Technologies](#technologies)
*   [How It Works](#how-it-works)
*   [Setup](#setup)
    *   [Requirements](#requirements)
    *   [Docker Setup](#docker-setup)
*   [Development Use](#development-use)
    *   [Backend (`backend`) and Queue (`queue`)](#backend-backend-and-queue-queue)
    *   [Frontend (`frontend`)](#frontend-frontend)
    *   [VS Code Tasks](#vs-code-tasks)
*   [Ports Used](#ports-used)
*   [Roadmap](#roadmap)
*   [Author](#author)

## Description

**Anime Scraper** is a comprehensive system for scraping, managing, and interacting with anime data. This monorepo is structured around three main components working together:

- **Anime Scraper API** (`backend`): A backend service built with FastAPI. It handles data scraping, processing, and storage (PostgreSQL/Redis). It provides the structured API endpoints for data retrieval and management.
- **Anime Scraper Frontend** (`frontend`): A web application developed with Next.js. It offers an intuitive interface for users to interact with the scraped data, manage collections, and access download features.
- **Dramatiq Workers** (`queue`): The asynchronous task processing system utilizing Dramatiq and Redis. It is responsible for heavy operations like web scraping and server-side downloading tasks.

Together, these components create a seamless solution for anime enthusiasts, simplifying the discovery and management of anime-related resources.

## Technologies

This project leverages a variety of modern technologies:

*   **Backend:** Python 3.10+, FastAPI, PostgreSQL, Redis, Dramatiq, ani-scrapy
*   **Frontend:** Next.js, React, TypeScript, NextAuth.js (AuthJS), npm/yarn
*   **Containerization:** Docker, Docker Compose
*   **Development Tools:** VS Code Tasks, uv (Python package manager)

## How It Works

This system leverages several technologies to provide a seamless experience:

- **Scraping**: The core scraping logic is handled by the external Python library [ani-scrapy](https://pypi.org/project/ani-scrapy/), which performs web scraping on anime websites (like AnimeFLV and JKAnime) to extract metadata and download links.
- **Data Persistence**: Anime metadata and user information are stored in a **PostgreSQL** database.
- **Asynchronous Processing**: Heavy tasks, such as initial data scraping and server-side episode downloads, are queued and processed asynchronously using **Dramatiq** workers, with **Redis** acting as the message broker.
- **User Interface**: The data is served via the FastAPI backend to the **Next.js** frontend, which provides the user interface. Authentication is managed using **NextAuth.js (AuthJS)**.

## Setup

### Requirements

To run this project, you need the following tools installed on your system:

-   **Docker** (Recommended for easy setup and deployment)
-   **Python 3.10+** (For backend and queue development without Docker)
-   **uv** or **pip** (Python package managers)
-   **Node.js 14+** (For frontend development without Docker)
-   **npm** or **yarn** (Node.js package managers)

### Docker Setup

The easiest way to get the entire system running is by using Docker Compose.

1.  Ensure Docker is running on your system.
2.  Build the images and start all services (API, Web, DB, Redis, Workers) using the following command at the root of the project:

    ```bash
    docker-compose up -d
    ```

3.  Access the services:
    -   **Web Frontend**: `http://localhost:4000` (or the port defined in `WEB_PORT`)
    -   **API Backend**: `http://localhost:4002` (or the port defined in `API_PORT`)

> [!TIP]
> If you are using `VSCode`, you can utilize the `Deploy with docker-compose` task.

## Development Use

> [!IMPORTANT]
> You need running `postgres` and `redis` databases for the backend services. These can be started via Docker Compose (`docker-compose up -d postgres redis`) or run locally.

#### Backend (`backend`) and Queue (`queue`)

1.  Navigate to the `backend` or `queue` directory:
    ```bash
    cd backend # or cd queue
    ```
2.  Install dependencies using `uv` (recommended) or `pip`:
    ```bash
    uv install # or pip install -r requirements.txt
    ```

#### Frontend (`frontend`)

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    The frontend will be accessible at `http://localhost:4000`.

#### VS Code Tasks

For easier development, VS Code tasks are defined in `.vscode/tasks.json`. You can run these tasks using `Ctrl+Shift+P` and typing `Run Task`.

## Ports Used

| Service                   | Port Used |
| ------------------------- | --------- |
| Web                       | `4000`    |
| Web Remote (Personal Use) | `4001`    |
| Api                       | `4002`    |
| PostgresSQL               | `4003`    |
| Redis                     | `4004`    |
| Flower                    | `4005`    |

## Roadmap

- [x] Get download link with web scraping
- [x] Create a web platform to manage and download anime epiosdes
- [x] Change to server side downloading
- [x] Upload anime scraper code as a library

## Author

- [Jonathan García](https://github.com/ElPitagoras14) - Computer Science Engineer