#!/usr/bin/env bash

# Auth Keys
export R5_AUTH_JWT_SECRET="abc-123"
export R5_AUTH_API_SECRET="abc-123"

# Api Keys
export GOOGLE_API_KEY="abc-123"

# Database
export R5_DRIVER="mysql+pymysql"
export R5_DATABASE_HOSTNAME="localhost:3307"
export R5_DATABASE_NAME="r5"
export R5_DATABASE_USER="user"
export R5_DATABASE_PASSWORD="password"

export R5_ENV="dev"

python -c "from r5 import Main; Main.cli.run()" start