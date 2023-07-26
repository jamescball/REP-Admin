FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install streamlit pandas mysql-connector-python python-dotenv

# Clone the public repository
RUN git clone https://github.com/jamescball/REP-Admin.git

# If you need files from the repository in your /app directory, you can copy them
# COPY REP-Admin/some-file .
COPY REP-Admin/* ./

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "Dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
