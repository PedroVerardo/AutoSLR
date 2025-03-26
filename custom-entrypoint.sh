#!/bin/bash
set -e

# Execute the default entrypoint script
/usr/local/bin/docker-entrypoint.sh "$@" &

# Wait for PostgreSQL to start
until pg_isready -U postgres -h localhost; do
  sleep 1
done

# Execute your SQL file
psql -U postgres -d article_search -f /path/to/your/script.sql

# Keep the container running
wait