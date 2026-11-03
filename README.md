# ml-labs

## 1. Project Overview

`ml-labs` is a Docker-based, reproducible Python lab environment for a hands-on Machine
Learning training. It provides a JupyterLab workspace with the core data science stack
(NumPy, Pandas, scikit-learn, Matplotlib) so that lab notebooks run consistently across
every participant's machine. Deep learning frameworks (PyTorch, TensorFlow) and GPU
support are intentionally out of scope and will live in a separate project.

## 2. Requirements

- Docker
- Docker Compose
- [uv](https://docs.astral.sh/uv/) (only needed for local, non-Docker dependency management)

## 3. Project Structure

```text
ml-labs/
├── pyproject.toml      # Project metadata and dependencies (managed by uv)
├── uv.lock              # Locked, reproducible dependency versions
├── Dockerfile            # CPU-only training image definition
├── compose.yaml         # Docker Compose service definition
├── .dockerignore
├── .gitignore
├── README.md
├── config/
│   └── settings.yaml    # Project-level configuration (no secrets)
├── labs/                 # Jupyter notebooks for training labs
├── data/                 # Datasets used by the labs
└── src/                   # Reusable Python code (preprocessing, training, evaluation)
```

## 4. Dependency Management with uv

Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. To work locally
without Docker:

```powershell
uv sync --locked
```

To add a new dependency:

```powershell
uv add <package-name>
```

This updates `pyproject.toml` and `uv.lock` together. Do not edit `uv.lock` by hand.

## 5. Running with Docker Compose

Build and start the lab environment:

```powershell
docker compose up --build
```

Run it in the background instead:

```powershell
docker compose up --build -d
```

## 6. Accessing JupyterLab

Once the container is running, check the logs for the access URL and token:

```powershell
docker compose logs ml-lab
```

Open the printed `http://127.0.0.1:8888/lab?token=...` URL in your browser. JupyterLab
is only reachable from `localhost` on the host machine.

## 7. Stopping Containers

```powershell
docker compose down
```

Project files in `labs/`, `data/`, and `src/` are bind-mounted into the container, so
your work is preserved on the host and survives container rebuilds.
