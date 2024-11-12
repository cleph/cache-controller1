from flask import Flask, request, jsonify
import redis
import pickle

from pymemcache import HashClient
from pymemcache.client.base import Client
import requests
import json

# Initialize Flask app
app = Flask(__name__)
with open("config.json") as config_file:
    config = json.load(config_file)

# Redis and Memcached clients
redis_client = redis.StrictRedis(
    host=config["redis"]["host"],
    port=config["redis"]["port"],
    db=config["redis"]["db"]
)

# Memcached client using multiple servers
memcache_servers = config["memcached"]["servers"]
memcache_client = HashClient(memcache_servers)

# API details for encryption and decryption
ENCRYPTION_API_URL = config["encryption_api"]["url"]['encrypt']
DECRYPTION_API_URL = config["encryption_api"]["url"]['decrypt']
API_TOKEN = config["encryption_api"]["token"]

# API details for encryption and decryption


# Helper function for encryption and decryption using external API
def encrypt_decrypt(text, action):
    url = ENCRYPTION_API_URL if action == 'encrypt' else DECRYPTION_API_URL
    payload_key = "text" if action == 'encrypt' else "encrypted_text"
    result_key = "encrypted_text" if action == 'encrypt' else "decrypted_text"
    payload = json.dumps({payload_key: text})
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }

    response = requests.post(url, headers=headers, data=payload)
    print(response.json())
    if response.status_code == 200:
        return response.json().get(result_key)  # assuming 'result' holds the encrypted/decrypted text
    else:
        raise Exception(f"Failed to {action}: {response.text}")

# Helper functions for Redis and Memcached
def set_redis(key, value, encrypted):
    # Encrypt the value if necessary
    stored_value = encrypt_decrypt(value, 'encrypt') if encrypted else value
    # Structure to store in Redis
    print(stored_value)
    data = {
        'text': stored_value,
        'encrypted': encrypted
    }
    # Serialize and store the JSON structure
    redis_client.set(key, pickle.dumps(data))
    return "Value set in Redis"

def get_redis(key):
    # Retrieve and deserialize the JSON structure from Redis
    stored_data = pickle.loads(redis_client.get(key))
    # Check if decryption is needed
    if stored_data['encrypted']:
        print(stored_data['text'])
        stored_data['text'] = encrypt_decrypt(stored_data['text'], 'decrypt')
    return stored_data['text']

def set_memcache(key, value, encrypted):
    # Encrypt the value if necessary
    stored_value = encrypt_decrypt(value, 'encrypt') if encrypted else value
    # Structure to store in Memcached
    data = {
        'text': stored_value,
        'encrypted': encrypted
    }
    # Serialize and store the JSON structure
    memcache_client.set(key=str(key), value=pickle.dumps(data))
    return "Value set in Memcached"

def get_memcache(key):
    # Retrieve and deserialize the JSON structure from Memcached
    stored_data = pickle.loads(memcache_client.get(str(key)))
    # Check if decryption is needed
    if stored_data['encrypted']:
        stored_data['text'] = encrypt_decrypt(stored_data['text'], 'decrypt')
    return stored_data['text']

# Main Data Handler
@app.route('/data', methods=['POST'])
def data_handler():
    data = request.json
    text = data.get('text', '')
    key = data.get('key')
    encrypted = data.get('encrypted', False)
    action = data.get('action', 'add')  # 'add' or 'get'
    storage_type = data.get('storage', 'redis')  # 'redis' or 'memcache'

    # Handle Add and Get operations
    if action == 'add':
        if storage_type == 'redis':
            message = set_redis(key, text, encrypted)
        elif storage_type == 'memcache':
            message = set_memcache(key, text, encrypted)
        else:
            return jsonify({"status": "error", "message": "Invalid storage type"}), 400
        return jsonify({"status": "success", "message": message}), 200

    elif action == 'get':
        if storage_type == 'redis':
            retrieved_data = get_redis(key)
        elif storage_type == 'memcache':
            retrieved_data = get_memcache(key)
        else:
            return jsonify({"status": "error", "message": "Invalid storage type"}), 400
        return jsonify({"status": "success", "data": retrieved_data}), 200

    # Encryption or Decryption
    elif action in ['encrypt', 'decrypt']:
        try:
            result = encrypt_decrypt(text, action)
            return jsonify({"status": "success", "result": result}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    else:
        return jsonify({"status": "error", "message": "Invalid action"}), 400

if __name__ == '__main__':
    app.run(debug=True)
