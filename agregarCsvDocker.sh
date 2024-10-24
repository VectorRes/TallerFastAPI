#creation of the database
docker-compose up -d
docker cp /root/TallerFastAPI/proyecto/avocado_filtrado.csv postgres_db:/avocado_filtrado.csv
psql -h localhost -p 3007 -U myuser -d avocado -f /root/TallerFastAPI/proyecto/dataBase.sql
