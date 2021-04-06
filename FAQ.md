# FAQ 
## Frequent error
### 1. Can't get car model please check cars.json
PSA API doesn't provide model for some vehicle. 
You should edit car.json and change label property like this:
```label: null > label: "e-208"```. 

Also check if your model is set in the ENERGY_CAPACITY variable in this [file](Car.py). 
If not please open an issue, or a pull request, so we can add your model to the list.

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
