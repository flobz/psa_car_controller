## Connect to OsmAnd API recipient

Use OsmAnd APR recipient - e.g. [Traccar](https://www.traccar.org) - to track your device

### Prerequisite
1. A working last version of psa_car_controller
2. Access to an OsmAnd API compatible receiver

### Procedure
1. Go to your OsmAnd receiver and setup a car which matches your VIN or use a self defined identifier
2. Enable OsmAndAPI for your car in "Control" section
3. stop psa_car_controller
4. edit config.json and check the following:
   4.1:
       "osmandapi": {
            "osmand_enable_vin": [
                "<VIN of you device - should automatically be here once activated in 2.>"
            ],
            "server_uri": "https://<your osmand api endpoint>"
        },
5. If you want to use a self defined identifier (you can skip this if you id should be your VIN): Open cars.json
    3.1: set osmand_id to you your chosen device id

    11.4 save the file

    11.5 restart psa_car_controller
6. Enjoy