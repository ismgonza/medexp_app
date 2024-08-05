bind = "0.0.0.0:8000"
module = "config.wsgi:application"

workers = 4  # Adjust based on your server's resources
worker_connections = 1000
threads = 4

certfile = "/etc/letsencrypt/live/vgclinic.com/fullchain.pem"
keyfile = "/etc/letsencrypt/live/vgclinic.com/privkey.pem"