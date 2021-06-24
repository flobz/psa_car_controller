FROM python:3-slim
ARG TARGETPLATFORM
COPY . /psa_car_controller/
WORKDIR /config
RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ] || [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        apt-get update && apt-get install -y gcc && apt-get clean ; \
        rm -rf /var/lib/apt/lists/* ; \
    fi ; \
    pip3 install --no-cache-dir -r /psa_car_controller/requirements.txt ; \
    apt-get remove -y gcc 2> /dev/null ; \
    apt-get autoremove -y
EXPOSE 5000
RUN chmod +x /psa_car_controller/docker_files/init.sh
ENV PSACC_BASE_PATH=/ PSACC_PORT=5000 PSACC_OPTIONS="-c -r --web-conf" PSACC_CONFIG_DIR="/config"
CMD /psa_car_controller/docker_files/init.sh
