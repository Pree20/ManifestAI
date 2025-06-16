import os
import snowflake.connector
from dotenv import load_dotenv
import uuid
from datetime import datetime
#from .snowflake_conn import get_snowflake_connection

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

print("DB:", os.getenv("SNOWFLAKE_DATABASE"))
print("SCHEMA:", os.getenv("SNOWFLAKE_SCHEMA"))

user=os.getenv('SNOWFLAKE_USER')
password=os.getenv('SNOWFLAKE_PASSWORD')
account=os.getenv('SNOWFLAKE_ACCOUNT')
warehouse=os.getenv('SNOWFLAKE_WAREHOUSE')
database=os.getenv('SNOWFLAKE_DATABASE')


def get_snowflake_connection(schema=None):
    schema = schema or os.getenv('SNOWFLAKE_SCHEMA')
    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        warehouse=warehouse,
        database=database,
        schema=schema
    )
    return conn




