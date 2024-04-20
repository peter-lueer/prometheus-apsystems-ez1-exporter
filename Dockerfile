FROM python:alpine

WORKDIR /app

#RUN pip install apsystems-ez1

COPY exporter.py /app/
COPY requirements.txt /app/
COPY objectlist.json /app/
COPY --chmod=0755 check_health.sh /app/
#COPY APsystemsEZ1 /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./exporter.py" ]

HEALTHCHECK --interval=90s CMD /app/check_health.sh

EXPOSE 9120