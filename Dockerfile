ARG PYTHON_DEP='python3 python3-wheel python3-typing-extensions python3-pandas python3-six python3-dateutil python3-brotli python3-pycryptodome libatlas3-base python3-cryptography python3-scipy androguard python3-flask python3-paho-mqtt python3-ruamel.yaml ca-certificates'
ARG DEBIAN_FRONTEND=noninteractive

FROM debian:bullseye-slim AS builder
ARG PYTHON_DEP
RUN  BUILD_DEP='python3-pip python3-setuptools python3-dev libblas-dev liblapack-dev gfortran' ; \
     apt-get update && apt-get install -y --no-install-recommends $BUILD_DEP $PYTHON_DEP;
RUN pip3 install --upgrade pip
RUN pip3 install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry export -f requirements.txt --output /tmp/requirements.txt
RUN pip3 install --no-deps --no-cache-dir --ignore-installed -r /tmp/requirements.txt
RUN poetry install
EXPOSE 5000

FROM debian:bullseye-slim
ARG PYTHON_DEP
WORKDIR /config
ENV PSACC_BASE_PATH=/ PSACC_PORT=5000 PSACC_OPTIONS="-c -r --web-conf" PSACC_CONFIG_DIR="/config" PYTHONPATH="/app"
COPY --from=builder /var/lib/apt /var/lib/apt
COPY --from=builder /var/cache/apt/ /var/cache/apt/
COPY --from=builder /usr/local/lib /usr/local/lib
RUN  apt-get install -y --no-install-recommends $PYTHON_DEP && \
     apt-get clean ; \
     rm -rf /var/lib/apt/lists/*
RUN mkdir app
COPY psa_car_controller /app/psa_car_controller
COPY /docker_files/init.sh /init.sh
CMD /init.sh