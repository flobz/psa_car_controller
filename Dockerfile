FROM python:3
RUN cd / && git clone https://github.com/flobz/psa_car_controller.git
WORKDIR /config
RUN pip3 install -r /psa_car_controller/requirements.txt
EXPOSE 8180
CMD /psa_car_controller/docker_files/init.sh
