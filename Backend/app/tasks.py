from database import celery_app, get_postgresql_connection, get_redis_connection
from sqlalchemy.orm import Session

@celery_app.task(name="tasks.example_task")
def example_task(data: str):
    """
    Example task that processes input data.
    """
    print(f"Processing data: {data}")
    return {"status": "success", "processed_data": data.upper()}

@celery_app.task(name="tasks.save_to_db")
def save_to_db(data: dict):
    """
    Save data to the PostgreSQL database asynchronously.
    """
    db = next(get_postgresql_connection())
    try:
        # Assume a 'Data' model exists
        new_data = Data(**data)
        db.add(new_data)
        db.commit()
        print(f"Data saved: {data}")
    except Exception as e:
        print(f"Failed to save data: {e}")
    finally:
        db.close()

@celery_app.task(name="tasks.upload_to_gcp")
def upload_to_gcp_task(file_path: str, bucket_name: str):
    """
    Upload a file from the local system to Google Cloud Storage.
    """
    from google.cloud import storage
    import os

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        file_name = os.path.basename(file_path)
        blob = bucket.blob(file_name)

        # Upload the file
        with open(file_path, "rb") as file_data:
            blob.upload_from_file(file_data)
        print(f"File uploaded to GCP: {file_name}")

        # Delete the local file after successful upload
        os.remove(file_path)
        print(f"Local file deleted: {file_path}")
    except Exception as e:
        print(f"Failed to upload file to GCP: {e}")
        raise
