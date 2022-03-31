# FAQ 
## Frequent error
### 1. Can't get car model
The car model need to be known by the app. To find it, the app use the first 10 character of your VIN.
If the car isn't in the list we need to add it, to do that you need to edit the file here:

Go to [car_models.yml](https://github.com/flobz/psa_car_controller/blob/develop/psa_car_controller/psacc/resources/car_models.yml)
and click on edit then copy cut and already existent model in the list and edit all properties that are incorrect for your model.
Finally, click on propose change. 

### 2. Error during activation {'newversion': '2.0.0', 'newversionurl': 'http://m.inwebo.com/', 'err': 'NOK:FORBIDDEN'}
Your psa account is locked because you makes 20 sms activation. To unlock do this : 
1. Install on a smartphone mypeugeot, myopel etc, depending on your car brand
2. If the application is already installed uninstall and reinstall
3. You should be asked to give your credentials
4. Connect and test remote control, it should say that you need to reset your account
6. If the remote control work on your smartphone it will work with psa_car_controller

### 3. No data in dashboard
The app record your position and other information if "-r" argument is provided and if data are fetched.

Data are fetched in the following scenarios:
- charge control is enabled with "-c" program argument
- refresh is enabled with "-R"
- You use "get_vehicleinfo" API endpoint


You need to make few trips to be able to see stats in the dashboard.

### 4. Permission error
It's happen if config file aren't writable by the user that launch the process.
To fix this go to the application directory and execute this command :
```
# if the user is launched by pi user do
sudo chown pi: -R . 
```

### 5. I don't receive SMS
The SMS authentication is used to be able to remote control your car.
 If your car doesn't have this functionality you should disable remote control when you start psa-car-controller 
by using `--remote-disable` argument.

### 6. SSL error
If you have an error more or less like this one:
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1056)
```
It's a problem on PSA server so don't open an issue, you can retry a second time and if it still doesn't work you just have to wait.
You can look to issue about this problem [here](https://github.com/flobz/psa_car_controller/search?q=ssl&type=issues).
