FROM python:3-slim
ARG TARGETPLATFORM
COPY . /psa_car_controller/
WORKDIR /config
RUN  apt-get update && apt-get install -y python3-typing-extensions python3-pandas python3-plotly python3-paho-mqtt \
        python3-six python3-dateutil python3-brotli  libblas-dev  liblapack-dev gfortran python3-pycryptodome \
        libatlas3-base python3-cryptography && \
         apt-get clean && rm -rf /var/lib/apt/lists/*
RUN  pip3 install --no-cache-dir -r /psa_car_controller/requirements.txt
EXPOSE 5000
ENV PSACC_BASE_PATH=/ PSACC_PORT=5000 PSACC_OPTIONS="-c -r --web-conf" PSACC_CONFIG_DIR="/config"
CMD /psa_car_controller/docker_files/init.sh
