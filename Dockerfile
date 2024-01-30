FROM python:3.7-slim-bullseye

RUN apt-get update --fix-missing && apt-get install -y libglib2.0-0 pkg-config cmake build-essential libgoogle-perftools-dev libsm6 libxext6 libxrender-dev poppler-utils libhdf5-dev pkg-config


ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . ./

RUN pip3 install --upgrade pip

RUN pip3 install --no-cache-dir -r ./requirements.txt

CMD exec uvicorn realup_server:app --host 0.0.0.0 --port $PORT