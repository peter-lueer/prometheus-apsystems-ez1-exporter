FROM python:alpine

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install apsystems-ez1

COPY exporter.py /app/
COPY APsystemsEZ1 /app/

CMD [ "python", "./exporter.py" ]

EXPOSE 9120