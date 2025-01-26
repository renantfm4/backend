

```sh
$ docker-compose up -d --build
$ docker-compose exec web alembic upgrade head
```

'sudo docker compose exec web poetry run alembic upgrade head'

sudo docker compose exec web poetry run alembic revision --autogenerate -m "hello migration"