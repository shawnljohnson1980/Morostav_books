server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP address

    # Redirect non-HTTPS traffic to HTTPS
    # Uncomment this if you set up SSL
    # if ($scheme != "https") {
    #     return 301 https://$host$request_uri;
    # }

    location / {
        proxy_pass http://127.0.0.1:8000;  # Django's default port, or your Gunicorn/WSGI server port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/static/files;  # Replace with the path to your static files
    }

    location /media/ {
        alias /path/to/your/media/files;  # Replace with the path to your media files
    }

    # Optionally, add SSL here if you have HTTPS setup (with a certificate and key)
    # ssl_certificate /path/to/your/certificate.pem;
    # ssl_certificate_key /path/to/your/private.key;
}

