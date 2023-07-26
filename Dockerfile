FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository into /app/REP-Admin
RUN git clone https://github.com/jamescball/REP-Admin.git

# Change the working directory to /app/REP-Admin
WORKDIR /app/REP-Admin

RUN ls

RUN pip install streamlit pandas mysql-connector-python python-dotenv

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "Dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
