import os
import boto3
from botocore.config import Config
from ..config import settings

AWS_REGION = settings.aws_region
S3_BUCKET = settings.s3_bucket
AWS_ACCESS_KEY = settings.aws_access_key
AWS_SECRET_KEY = settings.aws_secret_key

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)


def build_s3_key(user_id: str, verification_id: str, ext: str) -> str:
    return f"verifications/{user_id}/{verification_id}/photo{ext}"

def presign_put(key: str, content_type: str, expires_seconds: int = 300) -> str:
    return s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_seconds,
        HttpMethod="PUT",
    )

def presign_get(key: str, expires_seconds: int = 300) -> str:
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expires_seconds,
        HttpMethod="GET",
    )

def build_s3_uri(key: str) -> str:
    return f"s3://{S3_BUCKET}/{key}"

def parse_s3_uri(uri: str) -> str | None:
    prefix = f"s3://{S3_BUCKET}/"
    if uri.startswith(prefix):
        return uri[len(prefix):]
    return None

def object_exists(key: str) -> bool:
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except Exception:
        return False
