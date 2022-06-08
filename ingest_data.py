
import pandas as pd
from sqlalchemy import create_engine
import argparse
import os


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    #parquet_name = 'output.parquet'

    # Download the parquet file
    #os.system(f"wget {url} -o {parquet_name}")

    

    df = pd.read_parquet(f"{url}")

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    
    engine = create_engine(
        f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()

    print(pd.io.sql.get_schema(df, name='yellow_taxi', con=engine))
    df.to_sql(name=table_name, con=engine, if_exists='replace')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Ingest PARQUET data to Postgres')
    # user, password, host, port, database name, table name,
    # url of the parquet file
    parser.add_argument('--user', help='user name postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument(
        '--table_name', help='name of the table where we will write the results to')
    parser.add_argument('--url', help='url of the parquet file')
    args = parser.parse_args()
    main(args)
