FROM python:3.9
COPY . /app
WORKDIR /app
COPY requirements.txt ./
RUN pip install -U pip setuptools wheel
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN  export FLASK_APP=app.py
RUN export FLASK_ENV=development
EXPOSE 5000
ENTRYPOINT [ "python3","-m", "flask", "run","--host=0.0.0.0"]