#!/bin/bash
echo "Containerised psa_car_controller loading..."
cd "$PSACC_CONFIG_DIR"
python3 /psa_car_controller/server.py -p $PSACC_PORT -l 0.0.0.0 -b $PSACC_BASE_PATH $PSACC_OPTIONS
