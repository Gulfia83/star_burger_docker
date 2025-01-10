#!/bin/bash

set -e
cd /opt/star_burger
git pull
pip install -r requirements.txt
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
systemctl reload nginx
source star_burger/.env
curl -H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "production", "revision": "'"$(git rev-parse HEAD)"'", "rollbar_name": "star_burger", "local_username": "gulfia83", "status": "succeeded"}'
echo "Деплой завершен"
