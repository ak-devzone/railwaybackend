"""library_system package"""

# PyMySQL as MySQLdb replacement (pure Python, no system libs needed)
import pymysql
pymysql.install_as_MySQLdb()

# Import Celery app for Django
from .celery import app as celery_app

__all__ = ('celery_app',)
