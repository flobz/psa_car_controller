# Docker installation

A containerised version of the psa_car_controller Python scripts by Flobz.
- Docker Hub: https://hub.docker.com/r/flobz/psa_car_controller

### Overview
Once the container is running, the configuration of the psa_car_controller app is near-identical to setup instructions detailed in the app's readme.

You'll still need to make sure you have an apk for the appropriate Android app that it's attempting to use. The examples in this readme use the MyVauxhall app v1.27.1 from APKPure:
https://m.apkpure.com/myvauxhall-the-official-app-for-vauxhall-drivers/com.psa.mym.myvauxhall/download/2107-APK?from=versions%2Fversion

On your Docker host, create a config folder which will be mapped to the container and used to store all persistent data. Copy your APK into this folder.

### Installation
Create the container, detached, exposing port 5000, and mapping the a new config folder on your host to /config inside the container:

```
docker run -d -ti --name psa_car_controller1 \
  --publish 5000:5000 \
  -v /host_path/config:/config \
  --restart unless-stopped \
  psa_car_controller
```

Connect to the bash shell of the newly created container:
```
docker exec -it psa_car_controller1 /bin/bash
```

Inside the container, run the app_decoder.py script. You'll be prompted for the credentials you use to log into the app on your mobile device usually, plus your country code. If the script gives you a Success! message then move on:
```
python3 /psa_car_controller/app_decoder.py /config/com.psa.mym.myvauxhall_1.27.1.apk
```
Start server.py for a first run:
```
python3 /psa_car_controller/server.py -f /config/test.json -c /config/charge_config1.json -p 5000 -l 0.0.0.0 -r
```
You will be prompted to enter a code, sent by SMS to your registered mobile number, and the PIN for your account. Sometimes it asks twice (???), but once accepted the service should run. Allow it to run for about a minute before pressing ctrl+c to quit. You should end up back at the bash prompt within the container.

The final task is to update the container's configuration file to tell it to run the service automatically on next boot. This is done by editing /config/dockerconfig.conf and changing the SHELL_ONLY parameter to FALSE. Alternatively, paste the below command into your shell one by one. These will update the dockerconfig.conf file, exit the container's bash shell, stop the container, then restart the container.

```
echo "export SHELL_ONLY=\"FALSE\"" > /config/dockerconfig.conf
exit
docker stop psa_car_controller1
docker start psa_car_controller1
```
