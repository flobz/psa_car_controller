FROM python:3-slim
COPY . /psa_car_controller/
WORKDIR /config
RUN pip3 install --no-cache-dir -r /psa_car_controller/requirements.txt
EXPOSE 5000
RUN chmod +x /psa_car_controller/docker_files/init.sh
ENV PSACC_BASE_PATH=/ PSACC_PORT=5000
CMD /psa_car_controller/docker_files/init.sh
