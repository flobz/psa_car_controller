#!/bin/bash
echo "Containerised psa_car_controller loading..."
python3 /psa_car_controller/server.py -p 5000 -l 0.0.0.0 --web-conf
