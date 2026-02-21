# Installation Instructions for Celery & Redis

## Install Python Dependencies

```bash
pip install celery redis django-celery-beat
```

## Install Redis (Windows)

### Option 1: Using Memurai (Redis for Windows)
1. Download from: https://www.memurai.com/get-memurai
2. Install and start the service

### Option 2: Using WSL (Windows Subsystem for Linux)
```bash
wsl --install
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### Option 3: Using Docker
```bash
docker run -d -p 6379:6379 redis:latest
```

## Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

## Run Celery Worker

Open a new terminal in the backend directory:

```bash
celery -A library_system worker -l info --pool=solo
```

Note: Use `--pool=solo` on Windows

## Run Celery Beat (Scheduler)

Open another terminal in the backend directory:

```bash
celery -A library_system beat -l info
```

## Test Scheduled Tasks

### Manually Trigger Tasks

```python
# In Django shell
python manage.py shell

from api.tasks import send_daily_admin_report, send_weekly_admin_report

# Trigger daily report
send_daily_admin_report.delay()

# Trigger weekly report
send_weekly_admin_report.delay()
```

## Scheduled Times

- **Daily Report**: Every day at 9:00 AM IST
- **Weekly Report**: Every Monday at 9:00 AM IST

## Troubleshooting

### Redis Connection Error
- Make sure Redis is running: `redis-cli ping`
- Check CELERY_BROKER_URL in .env file

### Tasks Not Executing
- Check Celery worker logs
- Check Celery beat logs
- Verify timezone settings

### Email Not Sending
- Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env
- Verify ADMIN_EMAIL is set correctly
