# test-my-cluster-site
This is just a simple site to test out a self created Kubernetes cluster.

John McDonald (US)
Mon, May 4, 6:50 PM (2 days ago)
to me

my-project/

├── src/

│   ├── backend/

│   │   ├── app/

│   │   │   └── main.py

│   │   ├── Dockerfile

│   │   └── pyproject.toml

│   ├── frontend/

│   │   ├── app/

│   │   │   └── main.py

│   │   ├── Dockerfile

│   │   └── pyproject.toml

├── tests/

│   ├── backend/

│   │   └── test_main.py

│   └── frontend/

│       └── test_app.py

├── k8s/

│   ├── backend.yaml

│   ├── frontend.yaml

│   ├── ingress.yaml

│   └── registry-secret.yaml

├── .github/workflows/deploy.yaml

├── pyproject.toml

└── README.md

from fastapi import FastAPI

 

app = FastAPI()

 

@app.get("/")

def read_root():

    return {"message": "Hello World"}

----

 

[project]

name = "backend"

version = "0.1.0"

dependencies = [

    "fastapi",

    "uvicorn"

]

 

[build-system]

requires = ["hatchling"]

build-backend = "hatchling.build"

 

----

 

FROM python:3.11-bookworm

 

WORKDIR /app

 

COPY pyproject.toml .

RUN pip install uv && uv pip install .

 

COPY app ./app

 

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

 

----

import streamlit as st
import requests

st.title("Frontend")

try:
    response = requests.get(http://backend-service:8000/)
    data = response.json()
    st.write(data["message"])
except Exception as e:
    st.write("Backend not reachable")

👉 Calls backend via Kubernetes service

src/frontend/pyproject.toml

[project]
name = "frontend"
version = "0.1.0"
dependencies = [
    "streamlit",
    "requests"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

src/frontend/Dockerfile

FROM python:3.11-bookworm

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv && uv pip install .

COPY app ./app

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

🧪 4. TESTS (pytest)

tests/backend/test_main.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello World"

tests/frontend/test_app.py

def test_placeholder():
    assert True

🧱 5. KUBERNETES YAML (MicroK8s)

Kubernetes only runs images (not code)

k8s/backend.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: ghcr.io/yourname/backend:latest
          ports:
            - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
    - port: 8000
      targetPort: 8000

👉 Internal service (used by frontend)

k8s/frontend.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: ghcr.io/yourname/frontend:latest
          ports:
            - containerPort: 8501
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 8501

k8s/ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
spec:
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80

👉 Routes external traffic → frontend
Ingress is required for external access

k8s/registry-secret.yaml

apiVersion: v1
kind: Secret
metadata:
  name: ghcr-secret
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <BASE64>

👉 Allows cluster to pull private images

⚙️ 6. GITHUB ACTIONS (CI/CD)

.github/workflows/deploy.yaml

name: CI/CD

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Login to GHCR
        run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin

      - name: Build backend
        run: docker build -t ghcr.io/yourname/backend:latest ./src/backend

      - name: Build frontend
        run: docker build -t ghcr.io/yourname/frontend:latest ./src/frontend

      - name: Push images
        run: |
          docker push ghcr.io/yourname/backend:latest
          docker push ghcr.io/yourname/frontend:latest

      - name: Set kubeconfig
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > ~/.kube/config

      - name: Deploy
        run: |
          kubectl apply -f k8s/

👉 This implements:

CI: build + push images
CD: deploy to cluster
This matches standard Kubernetes pipelines: build → push → deploy

🌐 7. WHAT HAPPENS END-TO-END

Git push
  ↓
GitHub Actions
  ↓
Docker images built
  ↓
Images pushed to GHCR
  ↓
kubectl apply
  ↓
MicroK8s pulls images
  ↓
Pods start
  ↓
Ingress exposes frontend

🧠 Final Mental Model

This entire system works because:

Code → Docker Image → Registry → Kubernetes → Running App

NOT:

Code → Kubernetes

