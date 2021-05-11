# Installation
We need to get credentials from the android app.
We will retrieve this information:
 - client-id and client-secret  for the api
 - some url to login

1.1 Download the app on your computer, the original MyPeugeot app can be downloaded [here](https://apkpure.com/fr/mypeugeot-app/com.psa.mym.mypeugeot/download/2107-APK?from=versions%2Fversion) for example (please download version **1.27**).

1.2 Install requirements :

- You need **python >= 3.6**

- On debian based distribution you can install some requirement from repos, it's faster than installtion with pip: 
 
 ```
 sudo apt-get install python3-typing-extensions python3-pandas python3-plotly python3-paho-mqtt  python3-six python3-dateutil python3-brotli  libblas-dev  liblapack-dev gfortran python3-pycryptodome libatlas3-base python3-cryptography
 ```
    
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

1.4 If it works you will have VIN of your vehicles and there ids in the last line. 
The script generates a test.json file with all credentials needed.


            
1.5 start the app:
        
Start the app with charge control enabled :

``python3 server.py -f test.json -c charge_config1.json``

At the first launch you will receive an SMS, and you will be asked to give it and also give your pin code (the four-digit code that your use on the android app).
If it failed you can remove the file otp.bin and retry.

You can see all options available with :
``python3 server.py -h``
