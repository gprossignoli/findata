FROM python:3.9-buster

RUN apt-get -y update
RUN apt-get -y install git

RUN useradd --create-home findatauser

WORKDIR /home/findatauser/findata

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py  .
COPY .env .
RUN touch findata.log findata_errors.log
COPY src ./src

RUN chown -R findatauser .
RUN chmod -R 700 .

USER findatauser

ENTRYPOINT ["python", "main.py"]