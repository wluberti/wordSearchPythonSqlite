# word.whazza.nl






# Setup
Loosly based on https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-20-04

### Webserver (when not using Docker)
```
sudo apt update && sudo apt dist-upgrade
sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv nginx python3-certbot-nginx

python3 -m venv venv
source venv/bin/activate

pip install wheel uwsgi flask
```

### Basic (test) program
`main.py`
```
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
```

`wsgi.py` (rename `main` to whatever you called `main.py`)
```
from main import app

if __name__ == "__main__":
    app.run()
```

`project.ini`
```
[uwsgi]
; if you 'wsgi' refers to the name you gave 'wsgi.py' in file above.
module = wsgi:app

master = true
processes = 5

socket = myproject.sock
chmod-socket = 660
vacuum = true

die-on-term = true
```

`/etc/systemd/system/myproject.service`
```
[Unit]
Description=uWSGI instance to serve myproject
After=network.target

[Service]
User=CHANGEME
Group=www-data
; CHANGEME = the directory that contains your project (and has ./venv as environment directory)
WorkingDirectory=/CHANGEME
Environment="PATH=/CHANGEME/venv/bin"
ExecStart=/CHANGEME/venv/bin/uwsgi --ini project.ini

[Install]
WantedBy=multi-user.target
```

Starting all the files:
```
sudo systemctl start myproject
sudo systemctl enable myproject
sudo systemctl status myproject
```

### Nginx
```
server {
	server_name YOUR_DOMAIN_NAME;

	location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/YOUR_DOMAIN_NAME;
    }

	location / {
        include         uwsgi_params;
        uwsgi_pass      unix:/CHANGEME/myproject.sock;
	}

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/YOUR_DOMAIN_NAME/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/YOUR_DOMAIN_NAME/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}
server {
    if ($host = YOUR_DOMAIN_NAME) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

	listen 80;
	server_name YOUR_DOMAIN_NAME;
    return 404; # managed by Certbot
}
```

```
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
sudo systemctl restart nginx
sudo vim /etc/ferm/ferm.conf
sudo systemctl restart ferm
sudo certbot --nginx -d YOUR_DOMAIN_NAME
```

### Automaticaly restart service after deploy
`sudo visudo -f /etc/sudoers.d/restart_service`
```
USER HOST = (root) NOPASSWD: /bin/systemctl restart YOUR_SERVICE_NAME.service
```
