kill -9 $(ps -aef | grep gunicorn | grep -v grep | awk '{print $2}')
