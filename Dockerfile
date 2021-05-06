FROM python:3
RUN cd / && git clone https://github.com/flobz/psa_car_controller.git
WORKDIR /config
RUN pip3 install -r /psa_car_controller/requirements.txt
#RUN mkdir /config
##### These lines to be removed when merged with main psa_car_controller repo
RUN mkdir /psa_car_controller/docker_files
COPY docker_files/init.sh /psa_car_controller/docker_files
COPY docker_files/dockerconfig.conf /psa_car_controller/docker_files
##### End of temporary lines
EXPOSE 8180
CMD /psa_car_controller/docker_files/init.sh
