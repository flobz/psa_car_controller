FROM python:3-slim
ARG TARGETPLATFORM
COPY . /psa_car_controller/
WORKDIR /config
RUN  ARM_DEP='build-essential libssl-dev libffi-dev gcc g++ libblas-dev liblapack-dev gfortran rustc' ; \
     if [ "$TARGETPLATFORM" = "linux/arm/v7" ] || [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        apt-get update && apt-get install -y $ARM_DEP && apt-get clean ; \
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh && \
        rm -rf /var/lib/apt/lists/* ; \
     fi ; \
     pip3 install --no-cache-dir -r /psa_car_controller/requirements.txt && \
     apt-get remove -y $ARM_DEP 2> /dev/null ; \
     apt-get autoremove -y
EXPOSE 5000
ENV PSACC_BASE_PATH=/ PSACC_PORT=5000 PSACC_OPTIONS="-c -r --web-conf" PSACC_CONFIG_DIR="/config"
CMD /psa_car_controller/docker_files/init.sh
