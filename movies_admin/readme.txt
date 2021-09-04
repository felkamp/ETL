docker volume create --name postgres_data

для задания по api (с докером)
1. docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml up -d --build
-->http://127.0.0.1:8000/api/v1/movies/

для задания по nginx
1. docker-compose -f docker-compose.base.yml -f docker-compose.prod.yml up -d --build
-->http://127.0.0.1/admin