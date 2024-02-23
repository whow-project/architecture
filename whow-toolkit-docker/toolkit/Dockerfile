# immagine server ipopo
FROM python:3.8-slim
USER root
RUN apt-get update -y
RUN apt-get install -y git
RUN apt-get install -y unixodbc
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN python -m pip install git+https://github.com/anuzzolese/pyrml
COPY WHOWToolkit WHOWToolkit
RUN cp WHOWToolkit/triplestores/lib/odbc.ini etc/odbc.ini
RUN cp WHOWToolkit/triplestores/lib/libssl.so.1.1 /lib/x86_64-linux-gnu/
RUN cp WHOWToolkit/triplestores/lib/libcrypto.so.1.1 /lib/x86_64-linux-gnu/
WORKDIR /WHOWToolkit
EXPOSE 8765
EXPOSE 5000
#CMD ["python", "-m", "pelix.shell", "--run", "pelix.modules"]
CMD ["python", "whow-tk.py"]
