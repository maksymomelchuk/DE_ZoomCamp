
import pandas as pd
from sqlalchemy import create_engine


def ingest_callable(user, password, host, port, db, table_name, file_name, execution_date):

    print(table_name, file_name, execution_date)

    engine = create_engine(
        f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()

    print("Connection established successfully, reading data...")

    df = pd.read_parquet(f"{file_name}")

    print("Data readed to data frame, start processing data...")

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    print("Data types updated, start creating table with columns:")

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    print("Table created, start inserting data to table...")

    #print(pd.io.sql.get_schema(df, name=table_name, con=engine))

    print("Last message")

    df.to_sql(name=table_name, con=engine, chunksize=1000, if_exists='append')






def ingest_callable_fhv(user, password, host, port, db, table_name, file_name, execution_date):

    print(table_name, file_name, execution_date)

    engine = create_engine(
        f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()

    print("Connection established successfully, reading data...")

    df = pd.read_parquet(f"{file_name}")

    print("Data readed to data frame, start processing data...")

    #df.pickup_datetime = pd.to_datetime(df.pickup_datetime)
    #df.dropOff_datetime = pd.to_datetime(df.dropOff_datetime)

    print("Data types updated, start inserting to PostgreSQL database...")

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    print(pd.io.sql.get_schema(df, name=table_name, con=engine))
    df.to_sql(name=table_name, con=engine,
              if_exists='append', chunksize=50000)
