FROM postgres:16-alpine

# Enable useful extensions
COPY docker/postgres/init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
