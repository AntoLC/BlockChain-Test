FROM python:3

WORKDIR /usr/src/app

#ENV PATH="/venv/bin:$PATH"
#RUN python3 -m venv venv

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim"]

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /usr/src/app/Module1/

ENTRYPOINT [ "python" ]
CMD [ "main.py" ]