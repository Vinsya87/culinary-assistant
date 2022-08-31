# praktikum_new_diplom

проект по адресу http://51.250.100.40/ ИЛИ https://vinsteam.sytes.net/

файл с ключами .env разместить в infra/
# .env
# Укажите, что используете postgresql
DB_ENGINE=django.db.backends.postgresql
# Укажите имя созданной базы данных
DB_NAME=your_bd
# Укажите имя пользователя
POSTGRES_USER=your_user
# Укажите пароль для пользователя
POSTGRES_PASSWORD=password
# Укажите ваш хост или db(контейнер)
DB_HOST=127.0.0.1
# Укажите порт для подключения к базе
DB_PORT=5432
SECRET_KEY=ваш_секретный_ключ

клонировать репозиторий.
с папки infra/ выполнить команду sudo docker-compose up -d


Технологии
Django
Django DRF
PostgresSql
Docker
Docker-compose
Nginx
Workflow