#!/bin/bash
echo "Containerised psa_car_controller loading..."

echo "Checking for container configuration file /config/dockerconfig.conf"
FILE=/config/dockerconfig.conf
if [ -f "$FILE" ]; then
    echo "$FILE exists. Importing file..."
    source $FILE
else
    echo "$FILE does not exist. Setting default value for SHELL_ONLY=TRUE"
    export SHELL_ONLY="TRUE"
    echo "Copying default dockerconfig.conf file to /config"
    cp /psa_car_controller/docker_files/dockerconfig.conf /config
fi


if [ "$SHELL_ONLY" == "TRUE" ]
then
    echo "SHELL_ONLY = TRUE. Loading just a bash shell"
    /bin/bash
else
    echo "SHELL_ONLY = FALSE. Running server.py"
    python3 /psa_car_controller/server.py -f /config/test.json -c /config/charge_config1.json -p 5000 -l 0.0.0.0 -r
fi
