#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "Starting test stack..."
docker compose -f docker-compose.test.yml up -d --build

echo "Waiting for Redis..."
for i in {1..30}; do
  if docker compose -f docker-compose.test.yml exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo "Redis ready."
    break
  fi
  [ $i -eq 30 ] && { echo "Redis failed."; docker compose -f docker-compose.test.yml down; exit 1; }
  sleep 1
done

echo "Waiting for API..."
for i in {1..30}; do
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/health 2>/dev/null | grep -q 200; then
    echo "API ready."
    break
  fi
  [ $i -eq 30 ] && { echo "API failed."; docker compose -f docker-compose.test.yml down; exit 1; }
  sleep 1
done

export REDIS_URL=redis://localhost:6380
export QUEUE_NAME=test_queue
export PUBSUB_TEST_RESULT_KEY=test:echo:result
export PUBSUB_TEST_API_URL=http://localhost:5001

poetry run pytest -v
docker compose -f docker-compose.test.yml down
echo "Done."
