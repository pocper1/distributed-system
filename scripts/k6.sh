#!/bin/bash
export PGPASSWORD=123
docker exec -it postgres psql -U postgres_01 -d postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker cp ./DB/init_data.sql postgres:/init_data.sql
docker exec -it postgres psql -U postgres_01 -d postgres -f /init_data.sql

# run k6 tests
./k6.exe run --out dashboard k6/create_users_and_teams.js
# ./k6.exe run --out dashboard k6/test_file_upload.js
