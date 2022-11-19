#! /bin/bash

# Make sure no other instances of the system are running
docker-compose down 
# Remove database data to start the experiment from scratch
rm postgres/cinema_db_data -rf
rm postgres/security_db_data -rf
# Run docker-compose in background (-d option) so that we can automate queries
# docker-compose up --build -d
# Run docker-compose and see console output in real time
docker-compose up --build
# Shutting down all services
docker-compose down 
# Deleting all containers and images
#docker system prune -a 