FROM mongo:7-jammy

COPY mongod.conf /etc/mongod.conf

EXPOSE 27017

CMD ["mongod", "--config", "/etc/mongod.conf"]
