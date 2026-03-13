FROM postgres:16-alpine

# Enable useful extensions
COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
