"""library_system package"""

# PyMySQL as MySQLdb replacement (pure Python, no system libs needed)
import pymysql
# Fake version to satisfy Django 4.2+ requirement
pymysql.version_info = (2, 2, 1, 'final', 0)
pymysql.install_as_MySQLdb()

# Import Celery app for Django
from .celery import app as celery_app

__all__ = ('celery_app',)
