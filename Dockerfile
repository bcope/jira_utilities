FROM python:3.7
LABEL "Author"="Barrett Cope <dockerfile-author@barrettcope.com>"

COPY src /usr/local/bin/src
COPY requirements.txt /usr/local/bin/src/

RUN pip install -r /usr/local/bin/src/requirements.txt

ENTRYPOINT ["python", "/usr/local/bin/src/main.py"]
