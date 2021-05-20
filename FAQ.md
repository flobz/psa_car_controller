# FAQ 
## Frequent error
### 1. Can't get car model
Open an issue with [this template](https://github.com/flobz/psa_car_controller/issues/new?assignees=&labels=Car_model&template=can-t-get-car-model.md&title=%5BNew+Car+model%5D+my+model)
### 2. Error during activation {'newversion': '2.0.0', 'newversionurl': 'http://m.inwebo.com/', 'err': 'NOK:FORBIDDEN'}
Your psa account is locked because you makes 20 sms activation. To unlock do this : 
1. Install on a smartphone mypeugeot, myopel etc, depending on your car brand
2. If the application is already installed uninstall and reinstall
3. You should be asked to give your credentials
4. Connect and test remote control, it should say that you need to reset your account
6. If the remote control work on your smartphone it will work with psa_car_controller

### 3. No data to show
The app record your position if "-r" argument is provided.
You need to make few trips to be able to see stats in the dashboard.

### 4. Permission error
It's happen if config file aren't writable by the user that launch the process.
To fix this go to the application directory and execute this command :
```
# if the user is launched by pi user do
sudo chown pi: -R . 
```

### 5. I doesn't receive SMS
The SMS authentication is used to be able to remote control your car.
 If your car doesn't have this functionality you should disable remote control when you start psa-car-controller 
by using `--remote-disable` argument.
