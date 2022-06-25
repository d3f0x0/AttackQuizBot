# Quiz bot for learning MITRE ATT&CK

## Function:
 - Training your knowledge about MITRE ATT&CK
 - View your processing in learning MITRE ATT&CK

## Usage

### Create .env

Create file `touch ./bot/.env` which contains:

```
TOKEN=<TELEGRAM_TOKEN>
POSTGRES_DB=<DATABASE_NAME>
POSTGRES_NAME=<USER_NAME>
POSTGRES_PASSWORD=<USER_PASSWORD>
POSTGRES_PORT=<PORT_5432>
POSTGRES_HOST=<db_quiz>
GENERATE_DATA=<True>
```

### Updates environment

```
set -a
source app/.env
```

### Build docker-compose and start app as daemon

`docker-compose build`

`docker-compose up -d`

## Use library

| **Library**  | **Used**                        |
|--------------|---------------------------------|
| **pyattck**  | Generate data about MITRE ATT&CK |
| **psycopg2** | Working with PostgresSQL        |
| **aiogram**  | Working with Telegram API       |
| **logging**  | For logging                     |
| **dotenv**   | For get values from .env file   |

## Links

- [MITRE ATT&CK](https://attack.mitre.org/matrices/enterprise/)
- [PyAttck](https://github.com/swimlane/pyattck)
