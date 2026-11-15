# PSACC API
These links will work only if PSACC is on your computer, if it isn't please replace localhost by the ip of PSACC server.

1. Get the car state
    
   http://localhost:5000/get_vehicleinfo/YOURVIN

2. Get the car state from cache to avoid to use PSA API too much

   http://localhost:5000/get_vehicleinfo/YOURVIN?from_cache=1

3. Stop charge

   http://localhost:5000/charge_now/YOURVIN/0

4. Set hour to stop the charge to 6 am

   http://localhost:5000/charge_control?vin=YOURVIN&hour=6&minute=0 

5. Change car charge threshold to 80%

   http://localhost:5000/charge_control?vin=YOURVIN&percentage=80 

6. See the dashboard (only if record is enabled)

   http://localhost:5000

7. Refresh car state (ask car to send its state):

   http://localhost:5000/wakeup/YOURVIN

8. Start (1)/Stop (0) preconditioning

   http://localhost:5000/preconditioning/YOURVIN/1 or 0

9. Change charge hour (for example: set it to 22h30)

   http://localhost:5000/charge_hour?vin=YOURVIN&hour=22&minute=30

10. Honk the horn

    http://localhost:5000/horn/YOURVIN/count

11. Flash the lights (Duration is always roughly 10 seconds, regardless of set duration)

    http://localhost:5000/lights/YOURVIN/duration

12. Lock (1)/Unlock (0) the doors
   
    http://localhost:5000/lock_door/YOURVIN/1 or 0

13. Get config

    http://localhost:5000/settings

14. Change config parameter in config.ini (you need to restart the app after)

    http://localhost:5000/settings/electricity_config?night_price=0.2

    http://localhost:5000/settings/general?currency=%C2%A3

15. Get battery SOH

    http://localhost:5000/battery/soh/YOURVIN

16. Get the vehicle charging sessions
   
   http://localhost:5000/vehicles/chargings

17. Get the vehicle trips:
   
   http://localhost:5000/vehicles/trips

18. Get the preconditioning programs (returns 404 until the car has sent them, wake up the car first)

    http://localhost:5000/preconditioning_programs/YOURVIN

19. Save the preconditioning programs. All four programs are required, `day` has one 0/1 value per weekday.
    A running preconditioning is not stopped.

    ```
    curl -X POST http://localhost:5000/preconditioning_programs/YOURVIN \
      -H "Content-Type: application/json" \
      -d '{"program1": {"hour": 7, "minute": 30, "on": 1, "day": [1, 1, 1, 1, 1, 0, 0]},
           "program2": {"hour": 9, "minute": 0, "on": 0, "day": [0, 0, 0, 0, 0, 1, 1]},
           "program3": {"hour": 0, "minute": 0, "on": 0, "day": [0, 0, 0, 0, 0, 0, 0]},
           "program4": {"hour": 0, "minute": 0, "on": 0, "day": [0, 0, 0, 0, 0, 0, 0]}}'
    ```

20. Get the car's last answer to each remote command (`return_code` "0" means accepted)

    http://localhost:5000/remote_results/YOURVIN
