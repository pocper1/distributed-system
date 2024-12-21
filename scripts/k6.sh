#!/bin/bash

# Export PostgreSQL password
export PGPASSWORD=123

# Reset PostgreSQL database
docker exec -it postgres psql -U postgres_01 -d postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker cp ./DB/init_data.sql postgres:/init_data.sql
docker exec -it postgres psql -U postgres_01 -d postgres -f /init_data.sql

# Flush Redis
echo "Flushing Redis data..."
docker exec -it redis redis-cli FLUSHALL

# Run K6 tests
echo "Running K6 tests..."
./k6.exe run --out dashboard k6/create_users_and_teams.js
# Uncomment the following line to run additional K6 tests
# ./k6.exe run --out dashboard k6/test_file_upload.js
