# Etapa build
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

# Configurar las variables de entorno para la conexión a la base de datos
ENV R5_DATABASE_HOSTNAME librarydevserver.mysql.database.azure.com
ENV R5_DATABASE_NAME librarydev
ENV R5_DATABASE_USER admin1
ENV R5_DATABASE_PASSWORD Password1
ENV R5_DATABASE_SSL-MODE require

# Asegurarse de que pyodbc utilice los controladores de ODBC para SQL Server
ENV ODBCINI=/app/development/odbc.ini
ENV ODBCSYSINI=/app/development

ENTRYPOINT ["r5","start","--inet","0.0.0.0","--port","80"]

EXPOSE 80

