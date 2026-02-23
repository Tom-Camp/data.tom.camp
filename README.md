# 💾 Tom.Camp Data

A [FastAPI](https://fastapi.tiangolo.com/) application to serve data from the [Tom.Camp](https://tom.camp) 
website.

## Create device

```shell
docker run --rm \
--env-file \
.env \
-w /app \
datatomcamp-tcdata_api:latest \
uv run python scripts/create_device.py test_device
```