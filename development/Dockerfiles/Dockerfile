FROM python:3.10-bullseye AS build

WORKDIR /app

# -------------------------------------------------------------------------------------------------------------------- #
# Speedup Image build
# -------------------------------------------------------------------------------------------------------------------- #

RUN apt-get update && apt-get install -yq make && apt-get clean
COPY Makefile /app/Makefile
COPY development /app/development
RUN make deps/install

# -------------------------------------------------------------------------------------------------------------------- #
# Release
# -------------------------------------------------------------------------------------------------------------------- #


FROM build AS release

COPY . /app
RUN make project/install

ENTRYPOINT ["r5","start","--inet","0.0.0.0","--port","443","--ssl"]
