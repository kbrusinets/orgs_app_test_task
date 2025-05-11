# Organizations test task

## 🔧Requirements
- Docker Compose

## 🛠 Installation
1. Clone the repository
2. Ensure required ports are available
3. Run `docker-compose up -d` and wait for all services to start
4. Access the application - http://127.0.0.1:8080/docs
5. You can check the prepared db data in the alembic migration file

## 📊 Recommended checks 
- Search by coords - http://127.0.0.1:8000/api/v1/org/coords?lon=37.6102&lat=55.7616 
- Search by id - http://127.0.0.1:8000/api/v1/org/id?org_id=2
- Search by category (with tree) - http://127.0.0.1:8000/api/v1/org/category?cat_id=1
- Search by name ("%" wildcard is supported) - http://127.0.0.1:8000/api/v1/org/name?name=%25%D1%80%D0%BE%D0%B3%D0%B0%25
- Search by radius (only one building found) - http://127.0.0.1:8000/api/v1/org/radius?lon=37.6077&lat=55.7619&radius_meters=10
- Search by radius (multiple buildings found) - http://127.0.0.1:8000/api/v1/org/radius?lon=37.6077&lat=55.7619&radius_meters=100
- Search by rectangle area (only one building found) - http://127.0.0.1:8000/api/v1/org/area?lon=37.6077&lat=55.7619&height=10&width=10
- Search by rectanlge area (multiple buildings found) - http://127.0.0.1:8000/api/v1/org/area?lon=37.6077&lat=55.7619&height=100&width=100
