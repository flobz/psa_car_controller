# Remote Control of PSA car
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4b4b98fe6dc04956a1c9a07b97c46c06)](https://app.codacy.com/gh/flobz/psa_car_controller?utm_source=github.com&utm_medium=referral&utm_content=flobz/psa_car_controller&utm_campaign=Badge_Grade_Settings)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/f4082f146ad044bb900e1683035a540b)](https://www.codacy.com/gh/flobz/psa_car_controller/dashboard?utm_source=github.com&utm_medium=referral&utm_content=flobz/psa_car_controller&utm_campaign=Badge_Coverage)
[![Publish Docker image](https://github.com/flobz/psa_car_controller/actions/workflows/Docker_build.yml/badge.svg?branch=master)](https://hub.docker.com/repository/docker/flobz/psa_car_controller)
[![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/donate?hosted_button_id=SM652WPXFNCXS)
### This is a python program to control a psa car with connected_car v4 api. Using android app to retrieve credentials.
I test it with a Peugeot e-208, but it works with others PSA vehicles (Citroen, Opel, Vauxhall, DS).

With this app  you will be able to :
 - get the status of the car (battery level for electric vehicle, position ... )
 - start and stop the charge
 - set a charge threshold to limit the battery level to a certain percentage
 - set a stop hour to charge your vehicle only on off-peak hours
 - control air conditioning
 - control lights and horn if your vehicle is compatible (mine isn't) 
 - get consumption statistic
 - visualize your trips on a map or in a table
 - get the list of car charging  
 - visualize battery charging curve
 - visualize altitude trip curve
 - get car charging co2 emission
 - get car charging price
 - send live data to ABetterRoutePlanner

The official api is documented [here](https://developer.groupe-psa.io/webapi/b2c/quickstart/connect/#article) but it is not totally up to date, and contains some errors. 

A video in French was made by vlycop to explain how to use this application : https://youtu.be/XO7-N7G3biU 

For information on configuring the psa_car_controller Docker container [see this page]

 ## I. Installation
- [Installation on Linux or Windows](docs/Install.md)
- [Instalation as Home Assistant addon](https://github.com/flobz/psacc-ha/blob/main/psacc-ha/README.md)  
- [Installation in Docker](docs/Docker.md)
 ## II. Use the app
  
    2.1 Get the car state :
    http://localhost:5000/get_vehicleinfo/YOURVIN
    
    2.2 Get the car state from cache to avoid to use psa api too much
    http://localhost:5000/get_vehicleinfo/YOURVIN?from_cache=1

    2.2 Stop charge
    http://localhost:5000/charge_now/YOURVIN/0
    
    2.3 Set hour to stop the charge to 6am
    http://localhost:5000/charge_control?vin=yourvin&hour=6&minute=0 
    
    2.4 Change car charge threshold to 80 percent
    http://localhost:5000/charge_control?vin=YOURVIN&percentage=80 

    2.5 See the dashboard (only if record is enabled)
    http://localhost:5000
    
    2.6 Refresh car state (ask car to send its state):
    http://localhost:5000/wakeup/YOURVIN
    
    2.7 Start/Stop preconditioning
    http://localhost:5000/preconditioning/YOURVIN/1 or 0


## III. Use the dashboard
     
You can add the -r argument to record the position of the vehicle and retrieve this information in a dashboard.

``python3 server.py -f test.json -c charge_config1.json -r``
    
You will be able to visualize your trips, your consumption and some statistics:
    
     
![Screenshot_20210128_104519](https://user-images.githubusercontent.com/48728684/106119895-01c98d80-6156-11eb-8969-9e8bc24f3677.png)
- You have to add an api key from https://home.openweathermap.org/ in your config file, to be able to see your consumption vs exterior temperature.
- You have to add an api key from https://co2signal.com/ to have your C02 emission by KM (in France the key isn't needed). 
### IV. Charge price calculation
The dashboard can give you the price by kilometer and price by kw that you pay.
You just have to set the price in the config file.

After a successful launch of the app, a config.ini file will be created.
In this file you can set the price you pay for electricity in the following format "0.15".

If you have a special price during the night you can set "night price", "night hour start" and "night hour end". 
Hours need to be in the following format "23h12"?

You can modify a price manually in the dashboard. It can be useful if you use public charge point.
## V. Connect your home automation system:
- [Domoticz](docs/domoticz/Domoticz.md)
- [HomeAssistant](https://github.com/Flodu31/HomeAssistant-PeugeotIntegration)
- Jeedom (Anyone can share the procedure ?)

## FAQ
If you have a problem, or a question please check if the answer isn't in the [FAQ](FAQ.md). 
If you need information to contribute or edit this program go [here](docs/Develop.md).
## Connect to A better Route Planner
You can connect the app to ABRP, see [this page](docs/abrp.md)

## Donation
If you want to thank me for my work :smile:

[![donate](https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.com/donate?hosted_button_id=SM652WPXFNCXS)

