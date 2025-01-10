FROM python:3.10-slim

WORKDIR /opt/star-burger/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "3", "-b 0.0.0.0:8000", "star_burger.wsgi:application"]