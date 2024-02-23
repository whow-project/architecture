# Immagine airflow
#FROM apache/airflow:2.3.0-python3.9
FROM apache/airflow:2.6.3-python3.9
USER root
RUN apt-get update -y
RUN apt-get install -y python3-pyqt5
RUN apt-get install -y git


USER airflow
RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN python -m pip install git+https://github.com/anuzzolese/pyrml
EXPOSE 8080
#COPY virtodbc_r.so virtodbc_r.so
