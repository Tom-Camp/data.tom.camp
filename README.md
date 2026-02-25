# 💾 Tom.Camp Data

A [FastAPI](https://fastapi.tiangolo.com/) application to collect data from microcontrollers and store it in
a database. It provides an API for devices to send data and an admin endpoints to manage devices and view
collected data.

🔑 API keys are required for both devices and admin access. Devices can post data to the `/api/v1/data`
endpoint, while admins can manage devices and view data through the `/api/v1/devices` and `api/v1/keys`
endpoints.

The data that is collected is stored as a JSON blob in the database, allowing for flexible data structures.

## Installation

Clone the repository:

```bash
git clone git@github.com:Tom-Camp/data.tom.camp.git
```

Navigate to the project directory and install dependencies with [Astral uv](https://astral.sh/uv/):

```bash
cd data.tom.camp
uv sync install
```

Copy the `.env.example` file to `.env`; and update the environment variables:

```env
ADMIN_SECRET_KEY=your_secret_here
APP_NAME="Your.App.Name"
...
```

Start the application:

Using uv:

The application requires a running PostgreSQL database.

```bash
uv run main:app --reload
```

Using Docker Compose:

`docker-compose.yml` is configured to use the environment variables from the `.env` file and will spin
 up both the application and a PostgreSQL database. Make sure to update the `.env` file with the
 correct values.
```bash
docker-compose up -d
```

## Create devices

To create a device, you can use the admin API endpoint. First, generate a Device using the `/api/v1/devices`
endpoint. This will return a unique Device object, which can be used to authenticate when sending data.


## Send data

Devices can send data to the `/api/v1/data` endpoint using their unique Device ID and API key. The data
should be sent as a JSON payload in the request body. The Device ID and the API key should be included in the
request headers for authentication using the following format:

```
POST /api/v1/data HTTP/1.1
Host: your-app-domain.com
Content-Type: application/json
X-Device-ID: your_device_id
X-API-Key: your_api_key
```
