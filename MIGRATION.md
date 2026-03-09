# Data Migration

One-time migration of sensor data from the legacy MongoDB-based application to this PostgreSQL-based
application.

## Source Data

Export the data from the old application and save it as `devices.json` in the project root. The file
contains an array of devices, each with a nested array of data records.

## Running the Migration

**Dry run (no data written):**
```bash
uv run python migrate.py --dry-run
```

**Live migration:**
```bash
uv run python migrate.py
```

To use a different source file:
```bash
uv run python migrate.py --file /path/to/devices.json
```

## Running Against Production

Copy the required files to the server and run the script inside the api container:

```bash
scp devices.json migrate.py user@your-server:/var/www/subdomains/data.tom.camp/
ssh user@your-server
cd /var/www/subdomains/data.tom.camp
docker compose -f docker-compose.prod.yml exec api uv run python migrate.py
```

## Claude chats:

- `claude --resume "this application is starting correctly on the production server but I am
  getting 502 nginx error. th (Fork)"`

## Notes

- Original `created_date` timestamps from MongoDB are preserved.
- New UUIDs are generated for all records.
- The script is idempotent-safe only on a clean database — re-running against a populated database
  will fail on the unique `name` constraint for devices.

### Local Devices
