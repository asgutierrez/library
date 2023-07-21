#!/usr/bin/env bash

# Auth Keys
export R5_AUTH_JWT_SECRET="abc-123"
export R5_AUTH_API_SECRET="abc-123"

# Api Keys
export GOOGLE_API_KEY="abc-123"

# Database
export R5_DATABASE_HOSTNAME="librarydevserver.mysql.database.azure.com"
export R5_DATABASE_NAME="librarydev"
export R5_DATABASE_USER="admin1"
export R5_DATABASE_PASSWORD="Password1"
export R5_ENV="dev"
export R5_DATABASE_SSL-MODE="require"

python -c "from r5 import Main; Main.cli.run()" start
