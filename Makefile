build:
	 docker compose -f local.yml up --build -d --remove-orphans
up:
	 docker compose -f local.yml up -d

down:
	 docker compose -f local.yml down

down-v:
	 docker compose -f local.yml down -v

fintech-config:
	 docker compose -f local.yml config

makemigrations:
	 docker compose -f local.yml run --rm fintech python3 manage.py makemigrations

migrate:
	 docker compose -f local.yml run --rm fintech python3 manage.py migrate


collectstatic:
	 docker compose -f local.yml run --rm fintech python3 manage.py collectstatic --noinput

superuser:
	 docker compose -f local.yml run --rm fintech python3 manage.py createsuperuser

flush:
	 docker compose -f local.yml run --rm fintech python3 manage.py flush --noinput

network-inspect:
	 docker network inspect fintech_bank

fintech-db:
	docker compose -f local.yml exec postgres psql --username=admin --dbname=bank
