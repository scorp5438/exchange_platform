# Exchange App - Платформа для обмена вещами с удобным веб-интерфейсом (Так же имеется API)

Проект представляет собой web приложение для обмена вещами между пользователями.
Пользователи смогут размещать объявления о товарах для обмена,
просматривать чужие объявления и отправлять предложения на обмен.

## 🚀 Функционал

- **Аутентификация**:
    - Регистрация
- **Объявления**:
    - Можно создать объявление
    - Изменить объявление (только автор)
    - Удалить объявление (только автор или админ)
- **Предложение обмена**:
    - Можно откликаться на чужие объвления и предлагать в обмен вещь из своего
    - Подтверждать или отклонять предложение других пользователей
    - Редактировать комментарий и предложенное объявление в отправленном предложении
- **API/Админка**:
    - Реализовано api для интеграции в другие сервисы
    - Есть админ панель для управления данными (Объявления, категории, предложения обмена)
- **Тестирование** (unit по средствам django.test - TestCase)

## 🛠 Технологии

- **Backend**: Django (Python 3.12)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/Django%20REST-ff1709?style=for-the-badge&logo=django&logoColor=white)

- **База данных**: PostgreSQL

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

- **Деплой**: Docker + docker-compose

![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

- **Веб-сервер**: Nginx

![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)

## 📦 Установка

### Требования

- Docker 20.10+
- Docker Compose 2.0+

1. Клонируйте репозиторий:
```bash
   git https://github.com/scorp5438/exchange_platform.git
   cd exchange_platform
```
2. Установите зависимости
```bash
   pip install -r requirements.txt
```

3. Создайте файл .env на основе .env.template и заполните настройки:

```bash
   cp .env.template .env
   nano .env  # или отредактируйте в любом редакторе
```

4. Запустите сервисы через docker-compose:

```bash
   sudo docker-compose up -d --build
```

5. При первом запуске выполните миграции:

```bash
   sudo docker ps
   sudo docker exec -it {id контейнера web} python manage.py migrate
```  

    или зайти в контейнер и выполнить команду внутри

```bash
   sudo docker ps
   sudo docker exec -it {id контейнера web} /bin/bash
   python manage.py migrate
```     

6. Создайте суперпользователя (опционально):

```bash
   sudo docker exec {id контейнера web} python manage.py createsuperuser
```

    или зайти в контейнер и выполнить команду внутри

```bash
  sudo docker ps
  sudo docker exec -it {id контейнера fastapi} /bin/bash
  python manage.py createsuperuser
```

    и поочереди ввести email fullname и два раза password

7. Можно загрузить файл фикстур в базу данных (опционально)

```bash
  sudo docker ps
  sudo docker exec -it {id контейнера web} python manage.py loaddata data.json
```

    или зайти в контейнер и выполнить команду внутри

```bash
  sudo docker ps
  sudo docker exec -it {id контейнера web} /bin/bash
  python manage.py loaddata data.json
```

## Фикстуры содержат:

- **3 пользователя**:
    - admin
        - password 1234
    - pink_pony
        - password Qwerty741
    - blue_bug
        - password Qwerty741
- **3 Набор объявлений и предложений**

## 🔧 Использование

* Приложение доступно http://localhost:80/
* API: http://localhost:80/api/
* Админка Django: http://localhost:80/admin/

## 📌 API Endpoints  

### Объявления (`/api/ads/`)  
- `GET /api/ads/` — список объявлений (фильтрация: `?category=books&condition=new&search=книга`)  
- `POST /api/ads/` — создать объявление (требуется авторизация)  
- `GET /api/ads/{id}/` — детали объявления  
- `PUT /api/ads/{id}/` — обновить (только автор)  
- `DELETE /api/ads/{id}/` — удалить (автор или админ)  

### Предложения обмена (`/api/proposals/`)  
- `GET /api/proposals/` — список предложений (можно фильтровать по `sender_ad`, `receiver_ad`, `status`)  
- `POST /api/proposals/` — отправить предложение  
- `PATCH /api/proposals/{id}/` — изменить статус только получатель / обновить комментарий или предложенное объявление отправитель  

## 🧪 Тестирование

Находясь в папке с файлом manage.py выполнить команду

```
  python manage.py test
```

## ⚙️ Конфигурация

```ini
# Безопасность
DJANGO_SECRET_KEY=секретный ключ
DJANGO_DEBUG=Режим разработки или прод

# БД
POSTGRES_NAME_DB=имя дб
POSTGRES_USER_NAME=имя пользователя
POSTGRES_PASSWORD=пароль
POSTGRES_HOST=db
POSTGRES_PORT=5432 по дефолту
```
    



















