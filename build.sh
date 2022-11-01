#! /bin/bash

# Make sure no other instances of the system are running
docker-compose down 
# Remove database data to start the experiment from scratch
rm postgres/data -rf
rm postgres/security_db_data -rf
# Run docker-compose in background (-d option) so that we can automate queries
# docker-compose up --build -d
# Run docker-compose and see console output in real time
docker-compose up --build
#echo "Ricardo"
#sleep 10
#echo "Ricardo 2"
# Call to movies_cinema service
# curl localhost:8081/movies_cinema
# Shutting down all services
docker-compose down 

# ./setup.sh
# ./experiment1.sh
# ./experiment2.sh
# ./experiment3.sh