# Docker installation

A containerised version of the psa_car_controller.
- Docker Hub: https://hub.docker.com/r/flobz/psa_car_controller

### Overview
Once the container is running, the configuration of the psa_car_controller app is near-identical classic Linux/Windows installtion.

### Installation
Create the container, detached, exposing port 5000, and mapping config folder on your host to /config inside the container:

#### With docker-compose
```
docker-compose up -d
```
#### With Docker:
```
docker run -d -ti --name psa_car_controller1 \
  --publish 5000:5000 \
  -v /host_path/config:/config \
  --restart unless-stopped \
  flobz/psa_car_controller
```

Go to http://127.0.0.1:5000 and follow instruction
