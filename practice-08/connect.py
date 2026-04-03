import psycopg2
import config

def connect():
    return psycopg2.connect(
        host=config.host,
        dbname=config.dbname,
        user=config.user,
        password=config.password,
        port=config.port
    )