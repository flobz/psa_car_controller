# Installation

1.1 Download the app on your computer. 

1.2 Install requirements :

- You need **python >= 3.7**

- On debian based distribution you can install some requirement from repos, it's faster than installtion with pip: 
 
 ```
 sudo apt-get install python3-typing-extensions python3-pandas python3-plotly python3-paho-mqtt python3-six python3-dateutil python3-brotli libblas-dev  liblapack-dev gfortran python3-pycryptodome libatlas3-base python3-cryptography python3-pip
 ```
    
- For everyone :
      ```pip3 install psa-car-controller```
  
            
1.3 start the app:
        
Start the app with charge control enabled :

``psa-car-controller --web-conf``

At the first launch you will be asked to connect and give a code that you will receive by SMS and also give your pin code (the four-digit code that your use on the android app).
If it failed you can remove the file otp.bin and retry.

You can see all options available with :
``psa-car-controller -h``
