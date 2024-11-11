import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'aabbccddeeffgg')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:////var/lib/docker/volumes/datanavigatr-data/data-navi-gatr-data.db')
    SQLALCHEMY_BINDS = {
        'qdb1': os.environ.get('SQLALCHEMY_BINDS_QDB1', 'sqlite:////var/lib/docker/volumes/qdb1-data/qdb1-data.db')
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 80))
    SQL_QUERY_DIR = os.environ.get('SQL_QUERY_DIR', '/var/lib/docker/volumes/sql-queries/')
    DOWNLOADED_DB_PATH = os.environ.get('DOWNLOADED_DB_PATH', '/var/lib/docker/volumes/downloaded-data/')
