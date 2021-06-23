## Connect to A better Route Planner
 Thank's to this you will no longer have to edit manually:
- Exterior temperature
- Autonomy left
- Consumption 

ABRP will optimize your itinerary with these parameters.

### Prerequisite
1. A working last version of psa_car_controller
2. A abetterrouteplanner account
3. Make sure that you don't have a "Can't get car model error" if so look at the [FAQ](../FAQ.md)

### Procedure
1. Go to [https://abetterrouteplanner.com/](https://abetterrouteplanner.com/)
2. Edit the parameter of your car, you should have something like this:
![](abrp.png)
3. Click on Generic Link
4. Click on copy
5. Open the following url after replacing YOURTOKEN by the value you just copied:
```
http://localhost:5000/abrp?token=YOURTOKEN
```
7. Go to [http://localhost:5000](http://localhost:5000)
8. Click on control tab
9. Enable ABRP for your car
10. Open cars.json 
11. If abrp_name is null:
    
    11.1 Get the name from this list : [model list](https://api.iternio.com/1/tlm/get_carmodels_list?api_key=32b2162f-9599-4647-8139-66e9f9528370)
    
    11.2 stop the psa_car_controller 
    
    11.3 replace null with the correct name 
    
    11.4 save the file 
    
    11.5 restart psa_car_controller
12. Enjoy