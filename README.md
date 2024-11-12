
# Cache Controller

A Flask-based cache controller that integrates with Redis and Memcached to store and retrieve data, with optional encryption and decryption using an external API.

## Features
- Stores JSON data in Redis and Memcached.
- Optional encryption/decryption via external API.
- Retrieves data with automatic decryption based on stored data attributes.

## Requirements
- Python 3.x
- Redis and Memcached servers
- Docker (optional, for running Memcached on Windows)
- An external encryption API (e.g., https://enc.hardzon.com)

## Setup

### 1. Install Dependencies
First, clone the repository and navigate into the project folder:
```bash
git clone https://github.com/yourusername/cache-controller.git
cd cache-controller
```

Install required Python packages:
```bash
pip install -r requirements.txt
```

**Packages in `requirements.txt`:**
- `flask`
- `redis`
- `pymemcache`
- `requests`

### 2. Configure Redis
Ensure that Redis is running on your machine or server. If not already installed, download and install Redis following instructions on https://redis.io/download.

### 3. Set Up Memcached

#### Option 1: Using Docker (Recommended)
To run Memcached with Docker:
```bash
docker run -d -p 11211:11211 --name memcached memcached
```

#### Option 2: Running Memcached on Windows
If Docker is unavailable, download Memcached for Windows from https://github.com/nono303/memcached-win32.

Start Memcached from the command prompt:
```cmd
memcached.exe -d start
```

### 4. Configure API for Encryption and Decryption
The project uses an external API for encryption and decryption. Ensure you have an API token, and update `API_TOKEN` in `app.py`:
```python
API_TOKEN = "your_api_token_here"
```

### Running the Application
Run the Flask application:
```bash
python app.py
```

The app will start on http://localhost:5000.

## Usage

### Endpoints

#### 1. `POST /data`
Handles data storage and retrieval in Redis or Memcached with optional encryption.

**Request Parameters:**
- `key`: Key to store/retrieve the data.
- `text`: Data to store.
- `encrypted`: `true` or `false`, indicating whether the data should be encrypted.
- `action`: `add`, `get`, `encrypt`, or `decrypt`.
- `storage`: `redis` or `memcache`, to choose storage type.

**Example Requests:**

To **add** data to Redis:
```json
POST /data
{
  "key": "example_key",
  "text": "Your text",
  "encrypted": true,
  "action": "add",
  "storage": "redis"
}
```

To **retrieve** data from Redis:
```json
POST /data
{
  "key": "example_key",
  "action": "get",
  "storage": "redis"
}
```

## Troubleshooting

### Common Errors
- **Connection Error with Memcached**: Ensure Memcached is running. If on Windows, try using Docker or run `memcached.exe -d start` in the command prompt.
- **PermissionError with Socket**: Run the script as Administrator or ensure ports are open.

### Testing the Application
To test API connections for encryption/decryption:
```bash
curl -X POST http://localhost:5000/data -H "Content-Type: application/json" -d @request.json
```

Replace `request.json` with your test data.
