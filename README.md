# Remote Control of PSA car
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4b4b98fe6dc04956a1c9a07b97c46c06)](https://app.codacy.com/gh/flobz/psa_car_controller?utm_source=github.com&utm_medium=referral&utm_content=flobz/psa_car_controller&utm_campaign=Badge_Grade_Settings)
### This is a python program to control a psa car with connected_car v4 api. Using android app to retrieve credentials.
I test it with a Peugeot e-208 but it works with others PSA vehicles (Citroen, Opel, Vauxhall, DS).

With this app  you will be able to :
 - get the status of the car (battery level for electric vehicle, position ... )
 - start and stop the charge
 - set a charge threshold to limit the battery level to a certain percentage
 - set a stop hour to charge your vehicle only on off-peak hours
 - control air conditioning
 - control lights and horn if your vehicle is compatible (mine isn't) 
 - get consumption statistic
 - visualize your trips on a map
 
The official api is documented [here](https://developer.groupe-psa.io/webapi/b2c/quickstart/connect/#article) but it is not totally up to date, and contains some errors. 

A video in French was made by vlycop to explain how to use this application : https://youtu.be/XO7-N7G3biU 


## I. Get credentials
We need to get credentials from the android app.
We will retrieve these informations:
 - client-id and client-secret  for the api
 - some url to login

1.1 Download the app on your computer, the original MyPeugeot app can be downloaded [here](https://apkpure.com/fr/mypeugeot-app/com.psa.mym.mypeugeot/download/2107-APK?from=versions%2Fversion) for example (please download version 1.27).

1.2 Install requirements :

- On debian based distribution you can install some requirement from repos: 
 
 ```sudo apt-get install python3-typing-extensions python3-pandas python3-plotly python3-paho-mqtt  python3-six python3-dateutil python3-brotli  libblas-dev  liblapack-dev gfortran python3-pycryptodome python3-numpy libatlas3-base```
    
- For everyone :
      ```pip3 install -r requirements.txt```

1.3  run the decoder script : ```python3 app_decoder.py <path to my apk file>```
  
    mypeugeot email: <write your mypeugeot email>
    mypeugeot password: <write your mypeugeot password>
    What is the car api realm : clientsB2CPeugeot, clientsB2CDS, clientsB2COpel, clientsB2CVauxhall
    clientsB2CPeugeot
    What is your country code ? (ex: FR, GB, DE, ES...)
    FR
    save config change

    Your vehicles: {'VINNUBMER': {'id': 'vehicule id'}}

1.4 If it works you will have VIN of your vehicles and there ids in the last line. The script generate a test.json file with all credentials needed.

 ## II. Use the app
  
            
  1. start the app:
        
     Start the app with charge control enabled :

     ``python3 server.py -f test.json -c charge_config1.json``
     
     At the first launch you will receive a SMS and you will be asked to give it and also give your pin code (the four-digit code that your use on the android app).
     If it failed you can remove the file otp.bin and retry.
     
     You can see all options available with :
    ``python3 server.py -h``


  2. Test it 
  
    2.1 Get the car state :
    http://localhost:5000/get_vehicleinfo/YOURVIN
    
    2.2 Stop charge (only for solution 1)
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
### Charge price calculation
The dashboard can give you the price by kilometer and price by kw that you pay.
You just have to set the price in the config file.

After a successful launch of the app, a config.ini file will be created.
In this file you can set the price you pay for electricity in the following format "0.15".

If you have a special price during the night you can set "night price", "night hour start" and "night hour end". 
Hours need to be in the following format "23h12"?

You can modify a price manually in the dashboard. It can be useful if you use public charge point.
## IV. Connect your home automation system:
- [Domoticz](docs/domoticz/Domoticz.md)
- [HomeAssistant](https://github.com/Flodu31/HomeAssistant-PeugeotIntegration)
- Jeedom (Anyone can share the procedure ?)

## FAQ
If you have a problem, or a question please check if the answer isn't in the [FAQ](FAQ.md). 
## Connect to A better Route Planner
You can connect the app to ABRP, see [this page](docs/abrp.md)
## API documentation
The api documentation is described here : [api_spec.md](api_spec.md).
You can use all functions from the doc, for example :
```myp.api().get_car_last_position(myp.get_vehicle_id_with_vin("myvin"))```
## More information
To analyse the traffics between the app and psa server, you can use mitmproxy.
You will need the client certificate present in the apk at asssets/MWPMYMA1.pfx
```bash
# decrypt the pfx file (there is no password)
openssl pkcs12 -in MWPMYMA1.pfx -out MWPMYMA1.pem -nodes
```
Then you can use mitmproxy for example:

```
mitmproxy --set client_certs=MWPMYMA1.pem
```

## Donation
If you want you want to thank me for my work :smile:

[![donate](https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif)](https://www.paypal.com/donate?hosted_button_id=SM652WPXFNCXS)
