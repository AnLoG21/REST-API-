REST API для справочника Организаций, Зданий и Деятельностей

REST API приложение для управления справочником организаций, зданий и видов деятельности.

Архитектура

Проект использует многослойную архитектуру (Layered Architecture) с четким разделением ответственности:
- API Layer (routes/) - обработка HTTP запросов
- Service Layer (services/) - бизнес-логика
- Repository Layer (repositories/) - доступ к данным
- Model Layer (models/) - модели данных

Подробное описание архитектуры см. в ARCHITECTURE.md

Технологический стек

- FastAPI - веб-фреймворк для создания API
- SQLAlchemy - ORM для работы с базой данных
- Alembic - инструмент для миграций базы данных
- Pydantic - валидация данных
- PostgreSQL - база данных
- Docker - контейнеризация

Структура данных

Организация
- Название
- Несколько номеров телефонов
- Одно здание
- Несколько видов деятельности

Здание
- Адрес
- Географические координаты (широта, долгота)

Деятельность
- Название
- Иерархическая структура (дерево) с максимальным уровнем вложенности 3

API Endpoints

Все запросы требуют заголовок 'X-API-Key' с валидным API ключом.

Организации

- 'GET /organizations/{organization_id}' - Получить информацию об организации по ID
- 'GET /organizations' - Список организаций с фильтрами:
  - 'building_id' - фильтр по зданию
  - 'activity_id' - фильтр по виду деятельности (включая вложенные)
  - 'name' - поиск по названию
  - 'latitude', 'longitude', 'radius' - поиск по радиусу
  - 'min_lat', 'max_lat', 'min_lon', 'max_lon' - поиск по прямоугольной области

Здания

- 'GET /buildings' - Список всех зданий
- 'GET /buildings/{building_id}/organizations' - Список организаций в здании

Деятельности

- 'GET /activities/{activity_id}/organizations' - Список организаций по виду деятельности (включая вложенные)

Health Checks

- 'GET /health' - Проверка доступности API
- 'GET /health/ready' - Проверка готовности (включая подключение к БД)

Создание данных (для тестирования)

- 'POST /buildings' - Создать здание
- 'POST /activities' - Создать вид деятельности
- 'POST /organizations' - Создать организацию

Развертывание

Требования

- Docker и Docker Compose

Запуск приложения

1. Клонируйте репозиторий или скопируйте файлы проекта

2. Создайте файл '.env' (опционально, значения по умолчанию уже установлены):
   DATABASE_URL=postgresql://postgres:postgres@db:5432/organizations_db
   API_KEY=test-api-key-12345

3. Запустите приложение с помощью Docker Compose:
   docker-compose up --build

4. Приложение будет доступно по адресу: 'http://localhost:8001'

5. Документация API:
   - Swagger UI: 'http://localhost:8001/docs'
   - ReDoc: 'http://localhost:8001/redoc'

Использование API

Все запросы должны содержать заголовок 'X-API-Key':

curl -H 'X-API-Key: test-api-key-12345' http://localhost:8001/organizations

Примеры запросов

1. Получить все организации:
   curl -H 'X-API-Key: test-api-key-12345' http://localhost:8001/organizations

2. Получить организации в конкретном здании:
   curl -H 'X-API-Key: test-api-key-12345' http://localhost:8001/buildings/1/organizations

3. Получить организации по виду деятельности:
   curl -H 'X-API-Key: test-api-key-12345' http://localhost:8001/activities/1/organizations

4. Поиск организаций по названию:
   curl -G -H 'X-API-Key: test-api-key-12345' --data-urlencode 'name=Рога' 'http://localhost:8001/organizations'

5. Поиск организаций в радиусе:
   curl -H 'X-API-Key: test-api-key-12345' 'http://localhost:8001/organizations?latitude=55.7558&longitude=37.6173&radius=5'

Локальная разработка (без Docker)

1. Установите зависимости:
   pip install -r requirements.txt

2. Настройте PostgreSQL и создайте базу данных

3. Создайте файл '.env':
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/organizations_db
   API_KEY=test-api-key-12345

4. Выполните миграции:
   alembic upgrade head

5. Заполните базу тестовыми данными:
   python -m app.scripts.init_db

6. Запустите сервер:
   uvicorn app.main:app --reload

Тестовые данные

При первом запуске база данных автоматически заполняется тестовыми данными:
- 4 здания
- Дерево деятельностей (Еда -> Мясная/Молочная продукция, Автомобили -> Грузовые/Легковые/Запчасти -> Аксессуары)
- 5 организаций с различными комбинациями телефонов и деятельностей
