# Contributing to KiwiSSH <!-- omit in toc -->

Thanks for your potential interest in contributing to KiwiSSH! There are several ways you can help improve the project, whether it's through code contributions, documentation, bug reports, or feature requests.

## Table of Contents <!-- omit in toc -->

- [Code of Conduct](#code-of-conduct)
- [Development](#development)
  - [Setup Development Environment](#setup-development-environment)
    - [Local](#local)
    - [Build Docker images locally](#build-docker-images-locally)
  - [Swagger API Documentation](#swagger-api-documentation)
- [Commits](#commits)

---

## Code of Conduct

See the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) file for our code of conduct, which outlines our expectations for behavior and contributions to the project. Please read and follow the code of conduct to ensure a welcoming and inclusive environment for all contributors.

## Development

> [!IMPORTANT]
> If you are interested in contributing to the development of KiwiSSH, please create an issue and submit a pull request.
> For other inquiries, feel free to contact me -> [casudo](https://github.com/casudo)

Clone/download the repository and follow the [Setup Development Environment](#setup-development-environment) guide.

### Setup Development Environment

To set up a development environment for KiwiSSH, you can either run the backend and frontend locally or build the Docker images yourself. Below are instructions for both approaches.

#### Local

> [!IMPORTANT]
> You will need the following installed on your system:
>
> - Python 3.13+
> - Node.js v24.11+
> - npm 11.6+

To run KiwiSSH on your local machine without Docker, follow these steps:

1. Clone the repository
2. Navigate to the backend directory and install the required Python dependencies from `requirements.txt`
3. Set up the `kiwissh.yaml` configuration file in the `config/` directory
4. Run the backend using `python entrypoint.py`
5. Navigate to the frontend directory and install the dependencies with `npm install`
6. Start the frontend with `npm run dev`

#### Build Docker images locally

Prepare the Docker deployment files and configuration as described in the [Docker installation guide](README.md#docker), then use the development override to build the backend and frontend images from the local source tree:

```bash
docker compose \
  --env-file docker.env \
  -f docker-compose.yaml \
  -f docker-compose.dev.yaml \
  up -d --build
```

This builds:

- `kiwissh-backend:dev` from `backend/Dockerfile_backend`
- `kiwissh-frontend:dev` from `frontend/Dockerfile_frontend`

The frontend is available on port `8123`. The development override also exposes the backend API and Swagger UI at `http://<IP>:8000/docs`.

Rebuild after source changes with the same command. To force a clean rebuild:

```bash
docker compose \
  --env-file docker.env \
  -f docker-compose.yaml \
  -f docker-compose.dev.yaml \
  build --no-cache backend frontend
```

> [!TIP]
> The `.dockerignore` file is resolved from each build context root:
>
> - Backend: `backend/.dockerignore`
> - Frontend: `frontend/.dockerignore`
### Swagger API Documentation

The API documentation is available at `http://<IP>:8000/docs` when the backend is running. You can use this interface to explore and test the API endpoints.

## Commits

When contributing code, please follow these guidelines for commits:

- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format
- ruff for Python linting and formatting
- markdownlint for markdown linting
