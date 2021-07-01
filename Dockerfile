ARG PYTHON_DEP='python3 python3-wheel python3-typing-extensions python3-pandas python3-plotly python3-six python3-dateutil python3-brotli python3-pycryptodome libatlas3-base python3-cryptography python3-scipy androguard'

FROM debian:buster-slim AS builder
ARG PYTHON_DEP
RUN  BUILD_DEP='python3-pip python3-setuptools python3-dev libblas-dev liblapack-dev gfortran libatlas3-base' ; \
     apt-get update && apt-get install -y --no-install-recommends $BUILD_DEP $PYTHON_DEP;
COPY . /psa_car_controller/
RUN  pip3 install --system --no-cache-dir  -r /psa_car_controller/requirements.txt
EXPOSE 5000

FROM debian:buster-slim
ARG PYTHON_DEP
WORKDIR /config
ENV PSACC_BASE_PATH=/ PSACC_PORT=5000 PSACC_OPTIONS="-c -r --web-conf" PSACC_CONFIG_DIR="/config"
COPY --from=builder /var/lib/apt /var/lib/apt
COPY --from=builder /var/cache/apt/ /var/cache/apt/
COPY --from=builder /usr/local/lib /usr/local/lib
RUN  apt-get install -y --no-install-recommends $PYTHON_DEP && apt-get clean ; rm -rf /var/lib/apt/lists/*
COPY . /psa_car_controller/
CMD /psa_car_controller/docker_files/init.sh