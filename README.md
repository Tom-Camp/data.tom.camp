# 💾 Tom.Camp Data

A [FastAPI](https://fastapi.tiangolo.com/) application to serve data from the [Tom.Camp](https://tom.camp)
website.

## Create device

```shell
curl -X POST "http://localhost:8000/admin/devices?name=device1" \
  -H "X-Admin-Secret: your_secret_here"
```
