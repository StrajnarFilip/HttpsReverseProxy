#   Copyright 2022 Filip Strajnar
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import sys
import os
from subprocess import run

# Example invocation:
# python3 setup.py "my.domain.com" "my@email.com" "static"
# python3 setup.py "my.domain.com" "my@email.com" "proxy" "http://127.0.0.1:5000"
# python3 setup.py "my.domain.com" "my@email.com" "wordpress"

# First argument is domain
certificate_domain_name = sys.argv[1]
# Second is email
certificate_email = sys.argv[2]
# Static files or proxy (static OR proxy OR wordpress)
config_type = sys.argv[3]

# Quickly write to a file
def safe_write(file_path: str, content: str):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# Path to docker compose, which is responsible for creation of certificate
certificate_compose_path=os.path.join("Certbot","docker-compose.yaml")
# Path to NGINX default.conf
nginx_default_path=os.path.join("conf.d","default.conf")
# Path to NGINX https.conf
nginx_https_path=os.path.join("conf.d","https.conf")

# Render appropriate docker-compose.yaml for creation of certificate
safe_write(certificate_compose_path,f"""version: "3.0"
services:
  certbotcert:
    image: certbot/certbot
    ports:
      - "0.0.0.0:80:80"
      - "0.0.0.0:443:443"
    volumes:
      - ./letsencrypt:/etc/letsencrypt
      - ./var:/var
      - ./certificate:/certificate
      - ./script:/script
    environment:
      user_email: "{certificate_email}"
      user_domain: "{certificate_domain_name}"
    entrypoint: 'sh'
    command: "/script/script.sh"
""")

# Get certificate
try:
    os.chdir("Certbot")
    run(["docker-compose","up","-d"])
    os.chdir("..")
except:
    print("Failed to get certificate. Trying alternative.")
    try:
        run(["docker","compose","up","-d"])
        os.chdir("..")
    except:
        print("Failed to get certificate")

# Always redirect HTTP to HTTPS
safe_write(nginx_default_path,f"""server {{
    # Redirect to HTTPS
    listen 80 default_server;
    server_name  _;
    return 301 https://{certificate_domain_name};
}}
""")

if(config_type == "proxy"):
    # Location, example: http://127.0.0.1:5000
    location = sys.argv[4]

    safe_write(nginx_https_path,f"""server {{
    listen       443 ssl;
    server_name  {certificate_domain_name};
    ssl_certificate     /certificate/fullchain.pem;
    ssl_certificate_key /certificate/privkey.pem;
    ## Proxy to...
    location / {{
        proxy_set_header Host https://{certificate_domain_name};
        proxy_pass   {location};
    }}
}}""")

