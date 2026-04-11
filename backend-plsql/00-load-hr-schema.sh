#!/bin/sh
set -eu

SCHEMA_FILE="/docker-entrypoint-initdb.d/schema/01_SQL_Schema_HR.sql"
CONNECT_STRING="system/oracle@//localhost:1521/XEPDB1"

echo "Waiting for XEPDB1 to accept SYSTEM connections..."
until echo "EXIT" | sqlplus -s "$CONNECT_STRING" >/dev/null 2>&1; do
  sleep 2
done

echo "Importing HR schema into XEPDB1 as SYSTEM..."
sqlplus -s "$CONNECT_STRING" @"$SCHEMA_FILE"
