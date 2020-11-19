# Remote Control of PSA car
### This is a python program to control a psa car with connected_car v4 api. Using android app to retrieve credentials.
I test it with a Peugeot e-208 but it should work with others PSA vehicles.

With this app  you will be able to :
 - get the status of the car (battery level for electric vehicle, position ... )
 - start and stop the charge
 - set a charge threshold to limit the battery level to a certain percentage
 - set a stop hour to charge your vehicle only on off-peak hours
 - control air conditioning
 - control lights and horn if your vehicle is compatible (mine isn't) 
 
The api is documented [here](https://developer.groupe-psa.io/webapi/b2c/quickstart/connect/#article) but it is not totally up to date, and contains some errors. 


## I. Get credentials
We need to get credentials from the MyPeugeot app. You have two solutions :  
- You can extract all credentials from the application data after backup the app
- You can extract some credentials from the apk, it's faster but you will not be able to remote control your vehicle

1. Solution 1 : Backup MyPeugeot app
   
   We will retrieve those information:
     - client-id and client-secret  for the api
     - remote refresh token for the control of the vehicle

    1.1 MyPeugeot app doesn't allow backup by default so you need to modify it.
    Basically you need to put to true two attributes in the AndroidManifest.xml :
     - "android:allowBackup"
     - "android:extractNativeLibs"
     
        To do that you can follow this guide: https://forum.xda-developers.com/android/software-hacking/guide-how-to-enable-adb-backup-app-t3495117  
        The original app can be downloaded [here](https://apkpure.com/fr/mypeugeot-app/com.psa.mym.mypeugeot) for example.
        
    1.2 Uninstall the original app
    
    1.3 Install the modified app
    
    1.4 Login on the app and start a remote request (start preconditioning for example) to generate remote refresh token   
    
    1.5 Enable developer mode on your android phone 
    
    1.6 enable password for backup in developer option of your android phone (for some smartphone it is mandatory to successfully backup app)
    
    1.7 backup MyPeugeot app : 
    
    ``` adb backup -f backup.ab -noapk com.psa.mym.mypeugeot ```

    1.8. Retrieve credentials in the backup

    ```
   python3 app_decoder.py  backup.ab <backup_password>
   Calculated MK checksum (use UTF-8: true): XXXXXXXXXXXXX
    0% 1% 2% 3% 4% 5% 6% 7% 8% 9% 10% 11% 12% 13% 14% 15%  25% 26% 100% 
    235687424 bytes written to backup.tar.
    mypeugeot email: <write your mypeugeot email>
    mypeugeot password: <write your mypeugeot password>
    What is the car api realm : clientsB2CPeugeot, clientsB2CDS, clientsB2COpel, clientsB2CVauxhall
    clientsB2CPeugeot
    save config change

    Your vehicles: {'VINNUBMER': {'id': 'vehicule id'}} 
      ```
    1.9 If it works you will have VIN of your vehicles and there ids in the last line. The script generate a test.json file with all credentials needed.
 
2. Solution 2 : Extract credentials from the apk

    2.1 Download the app on your computer, the original app can be downloaded [here](https://apkpure.com/fr/mypeugeot-app/com.psa.mym.mypeugeot) for example.
    
    2.2 Install pythons dependency ```pip install androguard```
    
    2.3  run the decoder script : ```python3 app_decoder.py <path to my apk file>```
      
        mypeugeot email: <write your mypeugeot email>
        mypeugeot password: <write your mypeugeot password>
        What is the car api realm : clientsB2CPeugeot, clientsB2CDS, clientsB2COpel, clientsB2CVauxhall
        clientsB2CPeugeot
        save config change
    
        Your vehicles: {'VINNUBMER': {'id': 'vehicule id'}}
   
   2.4 If it works you will have VIN of your vehicles and there ids in the last line. The script generate a test.json file with all credentials needed.
 
 ## II. Use the app
  1. Install requirements
  ```pip3 install -r requirements.txt```
  2. start the app:
        
        if you choose solution 1 :
   ``python3 server.py -f test.json -c charge_control1.json`` 
        
        if you choose solution 2 :
   ``python3 server.py -f test.json`` 
 
  
  3. Test it 
  
    2.1 Get the car state :
    http://localhost:5000/get_vehicleinfo/YOURVIN
    
    2.2 Stop charge (only for solution 1)
    http://localhost:5000/charge_now/YOURVIN/0
    
    2.3 Set hour to stop the charge to 6am (only for solution 1)
    http://localhost:5000/charge_control?vin=yourvin&hour=6&minute=0 
    
    2.4 Change car charge threshold to 80 percent (only for solution 1)
    http://localhost:5000/charge_control?vin=YOURVIN&percentage=80 
           
## API specficication
The api spec is described here : [api_spec.md](api_spec.md).
You can use all fonction from the doc, for example :
```myp.api().get_car_last_position(myp.get_vehicle_id_with_vin("myvin"))```
## More information
To analyse the traffics between the app and psa server, you can use mitmproxy.
You will need the client certificate present in the apk at asssets/MWPMYMA1.pem

```mitmproxy --set client_certs=MWPMYMA1.pe```