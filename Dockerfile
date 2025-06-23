ARG DEBIAN_FRONTEND=noninteractive
FROM python:3.10-slim AS builder
WORKDIR /tmp
COPY ./pyproject.toml /tmp/
COPY ./psa_car_controller/ /tmp/psa_car_controller/
RUN pip3 install --break-system-packages --upgrade pip wheel setuptools build
RUN python3 -m build

EXPOSE 5000
FROM python:3.10-slim
ARG PSACC_VERSION="0.0.0"
WORKDIR /config
ENV PSACC_BASE_PATH=/ PSACC_PORT=5000 PSACC_OPTIONS="-c -r --web-conf" PSACC_CONFIG_DIR="/config" PYTHONPATH="/app"
COPY --from=builder /tmp/dist/ /config/dist/
RUN pip3 install --break-system-packages dist/psa_car_controller-${PSACC_VERSION}-py3-none-any.whl
RUN rm -r /config/dist
COPY /docker_files/init.sh /init.sh
CMD [ "/init.sh" ] 
