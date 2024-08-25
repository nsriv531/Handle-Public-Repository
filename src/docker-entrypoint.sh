#!/bin/bash

ENV="${DEPLOY_ENV:-prod}"
PYTHONPATH=${PYTHONPATH}:/:/src/

echo "Environment: ${ENV}"
echo "User: $(whoami)"
echo "PATH: ${PATH}"
echo "PYTHONPATH: ${PYTHONPATH}"
echo "DEBUG: ${DEBUG}"

if [ "${ENV}" == "dev" ]; then
#  npm run vite-dev
	python manage.py runserver 0.0.0.0:8000
else
  npm run vite-build
  python manage.py collectstatic --noinput
	uwsgi --ini /conf/uwsgi_docker_prod.ini
fi
