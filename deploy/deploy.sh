set -e

rsync -avz \
  --exclude='.venv/' \
  --exclude='minio/' \
  --exclude='postgres/' \
  --exclude='.env' \
  --exclude='.env.example' \
  --exclude='.git' \
  --exclude='transform/target/' \
  --exclude='transform/logs/' \
  --exclude='logs/' \
  ../ alwyzon@203.34.137.202:/home/alwyzon/techmunkak

ssh -tt -o StrictHostKeyChecking=no alwyzon@203.34.137.201 "cd /home/alwyzon/techmunkak && docker compose -f docker-compose.yml -f docker-compose.prod.yml down --remove-orphans"
ssh -tt -o StrictHostKeyChecking=no alwyzon@203.34.137.201 "cd /home/alwyzon/techmunkak && docker compose -f docker-compose.airflow.yml down --remove-orphans"
ssh -tt -o StrictHostKeyChecking=no alwyzon@203.34.137.201 "cd /home/alwyzon/techmunkak && docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"
ssh -tt -o StrictHostKeyChecking=no alwyzon@203.34.137.201 "cd /home/alwyzon/techmunkak && docker compose -f docker-compose.airflow.yml up -d --build"