# Docker: Local Development Databases

Spins up MySQL (main data) and MongoDB (search query logs)
in containers. The console application itself is not
packaged in Docker—it continues to run as a standard Python process on the host
and connects to the databases via `localhost`.

## A single `../.env` for everything

`docker compose` automatically picks up `../.env` from the repository root—
this is the same file used by the Python application. Copy
`.env.example` to `.env`; that is all you need to do—no changes are
required for local development. If you want to change a password (e.g.,
`MYSQL_EDIT_PASSWORD`), you only need to change it once in `.env`, and the
update will apply to both the container (upon the next initialization)
and the application.

⚠️ The init script `docker/mysql-init/01-create-users.sh` creates
read/edit users **only during the first startup** (when the data directory is empty).
If you change the password in `../.env` after the initial startup, the old
password inside the container will not update automatically; you must either
recreate the database (see "If you need to recreate everything" below) or
manually change the user's password using `ALTER USER`.

## Data is stored on the disk, not in a Docker volume

Both containers are mounted to actual folders on the `D:` drive:

```
D:\DB\bookstore\mysql   -> MySQL data
D:\DB\bookstore\mongo    -> MongoDB data
```

This means that running `docker compose down` (without `-v`)—or even deleting the containers—will 
not result in data loss, as the data physically resides in `D:\DB`. If you need to start "from 
scratch," simply stop the containers and manually delete the contents of the corresponding folder.

It is recommended to create these folders before the initial startup:

```powershell
mkdir D:\DB\bookstore\mysql
mkdir D:\DB\bookstore\mongo
```

## Launch

```bash
docker compose up -d
```

The first time MySQL starts, it will execute `docker/mysql-init/01-create-users.sh`, creating 
the `bookstore_read` and `bookstore_edit` users with the appropriate privileges (see the file 
itself). This happens **only when the data directory is empty**; if `D:\DB\bookstore\mysql` 
already contains data from a previous run, the init script will not execute again.

To verify that the databases have started up and are ready to accept connections:

```bash
docker compose ps
```

(status is `healthy` — ready to connect)

## Connecting from the application

`../.env.example` already contains credentials matching this `docker-compose` setup:
copy it to `.env` — no changes are needed for local development.

| Variable in `../.env` | Where it goes |
|---|---|
| `MYSQL_READ_USER` / `MYSQL_READ_PASSWORD` | container `mysql`, port 3306 |
| `MYSQL_EDIT_USER` / `MYSQL_EDIT_PASSWORD` | container `mysql`, port 3306 |
| `MONGO_URI@localhost:27017` | container `mongo`, port 27017 |


## Stopping

```bash
docker compose down          # containers are removed; data in D:\DB remains
docker compose down -v       # same as above + removes named volumes
```

## If need to recreate everything

```bash
docker compose down
# manually clear D:\DB\mysql and D:\DB\mongo
docker compose up -d
```
