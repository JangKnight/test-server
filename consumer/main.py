import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from io import BytesIO

import aio_pika
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET = os.getenv("MINIO_BUCKET", "events")
FLUSH_INTERVAL = int(os.getenv("FLUSH_INTERVAL", "300"))
FLUSH_COUNT = int(os.getenv("FLUSH_COUNT", "100"))

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

buffer = []


def build_object_key(now: datetime) -> str:
    return (
        f"year={now.year}/month={now.month:02d}/"
        f"day={now.day:02d}/hour={now.hour:02d}/{uuid.uuid4()}.parquet"
    )


def write_to_minio(batch: list):
    now = datetime.now(timezone.utc)
    table = pa.Table.from_pylist(batch)

    parquet_buffer = BytesIO()
    pq.write_table(table, parquet_buffer)

    s3_client.put_object(
        Bucket=BUCKET,
        Key=build_object_key(now),
        Body=parquet_buffer.getvalue(),
    )
    print(f"Wrote {len(batch)} events to MinIO")


async def flush_buffer():
    if not buffer:
        return
    batch = buffer[:]
    buffer.clear()
    write_to_minio(batch)


async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process():
        event = json.loads(message.body)
        buffer.append(event)
        if len(buffer) >= FLUSH_COUNT:
            await flush_buffer()


async def flush_on_interval():
    while True:
        await asyncio.sleep(FLUSH_INTERVAL)
        await flush_buffer()


async def main():
    try:
        s3_client.head_bucket(Bucket=BUCKET)
    except Exception:
        s3_client.create_bucket(Bucket=BUCKET)

    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=FLUSH_COUNT)
    queue = await channel.declare_queue("events", durable=True)

    await queue.consume(handle_message)
    asyncio.create_task(flush_on_interval())

    print("Consumer running...")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
