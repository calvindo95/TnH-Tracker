gunicorn server:server -b 0.0.0.0:8050 -D --log-file=/home/pi/TnH-Tracker/gunicorn.log --log-level=DEBUG --timeout 90
