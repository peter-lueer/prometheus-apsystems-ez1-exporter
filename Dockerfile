FROM python:alpine

WORKDIR /app

#RUN pip install apsystems-ez1

COPY exporter.py /app/
COPY requirements.txt /app/
COPY objectlist.json /app/
#COPY APsystemsEZ1 /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./exporter.py" ]

EXPOSE 9120