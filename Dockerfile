FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt ./
COPY clcone_lab clcone_lab
COPY malignant_agent malignant_agent
COPY gao_orchestrator gao_orchestrator

RUN pip install --upgrade pip && \
    pip install .

COPY docs docs
COPY tests tests

CMD ["python", "-m", "clcone_lab.CLcone_Assays"]

