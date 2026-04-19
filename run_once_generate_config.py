"""
run_once_generate_config.py
Run this once to create config.yaml with hashed passwords.
"""

import yaml
import bcrypt

USERS = {
    "admin": {
        "name":     "Admin User",
        "email":    "admin@datafusion.io",
        "password": "Admin1234!",
    },
    "analyst": {
        "name":     "Data Analyst",
        "email":    "analyst@datafusion.io",
        "password": "Analyst1234!",
    },
}

credentials = {"usernames": {}}

for username, data in USERS.items():
    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
    credentials["usernames"][username] = {
        "name":     data["name"],
        "email":    data["email"],
        "password": hashed,
    }

config = {
    "credentials": credentials,
    "cookie": {
        "expiry_days": 7,
        "key":  "datafusion_super_secret_key_CHANGE_ME",
        "name": "datafusion_auth_cookie",
    },
}

with open("config.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

print("config.yaml created successfully!\n")
print("Login credentials:")
for username, data in USERS.items():
    print(f"  username: {username}   password: {data['password']}")
