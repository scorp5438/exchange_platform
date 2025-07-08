FROM python:3.12

RUN useradd -m user_admin

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip cache purge

COPY . .

RUN chown -R user_admin:user_admin /app

USER user_admin

RUN python manage.py collectstatic --noinput

CMD ["sh", "-c", "gunicorn exchange_platform.wsgi:application --bind 0.0.0.0:8000 --workers 3"]