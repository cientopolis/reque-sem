FROM python:3.9
COPY . /app
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN  export FLASK_APP=app.py
RUN export FLASK_ENV=development
EXPOSE 5000
ENTRYPOINT [ "python","-m", "flask", "run","--host=0.0.0.0"]