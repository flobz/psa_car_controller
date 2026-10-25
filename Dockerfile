ARG PYTHON_DEP='python3 python3-pandas python3-six python3-dateutil python3-brotli libatlas3-base python3-lxml python3-yaml python3-flask python3-paho-mqtt python3-ruamel.yaml ca-certificates python3-numpy'
# python3-scipy depends on pythran, which pulls in gcc, g++ and boost; only the builder installs it
ARG SCIPY_RUNTIME_DEP='python3-decorator libgfortran5 liblbfgsb0 libblas3 liblapack3'
ARG DEBIAN_FRONTEND=noninteractive
FROM debian:bookworm-slim AS builder
ARG PYTHON_DEP
RUN  BUILD_DEP='python3-pip python3-setuptools python3-dev libblas-dev liblapack-dev gfortran libffi-dev libxml2-dev libxslt1-dev make automake gcc g++ subversion ninja-build' ; \
     apt-get update && apt-get install -y --no-install-recommends $BUILD_DEP $PYTHON_DEP python3-scipy;
ARG PSACC_VERSION="0.0.0"
RUN pip3 install --break-system-packages --upgrade pip wheel setuptools
COPY ./dist/psa_car_controller-${PSACC_VERSION}-py3-none-any.whl .
RUN pip3 install --break-system-packages --no-cache-dir psa_car_controller-${PSACC_VERSION}-py3-none-any.whl && \
    python3 -m pip uninstall -y --break-system-packages pip wheel setuptools && \
    mkdir /scipy && cp -a /usr/lib/python3/dist-packages/scipy /usr/lib/python3/dist-packages/scipy-*.dist-info /scipy/
EXPOSE 5000

FROM debian:bookworm-slim
ARG PYTHON_DEP
ARG SCIPY_RUNTIME_DEP
WORKDIR /config
ENV PSACC_BASE_PATH=/ PSACC_PORT=5000 PSACC_OPTIONS="-c -r --web-conf" PSACC_CONFIG_DIR="/config" PYTHONPATH="/app"
RUN  apt-get update && \
     apt-get install -y --no-install-recommends $PYTHON_DEP $SCIPY_RUNTIME_DEP curl && \
     apt-get clean && \
     rm -rf /var/lib/apt/lists/*
COPY --from=builder /scipy/ /usr/lib/python3/dist-packages/
COPY --from=builder /usr/local/lib /usr/local/lib
COPY --from=builder /usr/local/bin/  /usr/local/bin/

# Install the Chromium headless shell and its dependencies (Playwright is not installed on armv7)
RUN (command -v playwright >/dev/null && \
     playwright install --with-deps --only-shell chromium || \
     echo "Playwright not available on this architecture, headless auth will use manual fallback") && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY /docker_files/init.sh /init.sh
CMD /init.sh
