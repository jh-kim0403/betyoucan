import boto3
import logging
from botocore.exceptions import ClientError
from ..config import settings

_ses = boto3.client(
    "ses",
    region_name=settings.aws_region,
    aws_access_key_id=settings.ses_access_key,
    aws_secret_access_key=settings.ses_secret_key,
)


def send_verification_email(to_email: str, first_name: str, token: str) -> None:
    verification_url = f"betyoucan://verify-email?token={token}"
    try:
        _ses.send_email(
            Source=settings.sender_email,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": "Verify your Bet You Can email"},
                "Body": {
                    "Html": {
                        "Data": (
                            f"<p>Hi {first_name},</p>"
                            f"<p>Click the link below to verify your email. "
                            f"This link expires in 24 hours.</p>"
                            f'<p><a href="{verification_url}">{verification_url}</a></p>'
                        )
                    },
                    "Text": {
                        "Data": (
                            f"Hi {first_name},\n\n"
                            f"Verify your email by visiting:\n{verification_url}\n\n"
                            f"This link expires in 24 hours."
                        )
                    },
                },
            },
        )
    except ClientError:
        logging.exception("SES failed to send verification email to %s", to_email)
        raise
