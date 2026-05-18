from typing import Any

import stripe


class StripeWebhookError(Exception):
    pass


def construct_webhook_event(
    payload: bytes, sig_header: str, webhook_secret: str
) -> dict[str, Any]:
    try:
        return stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret,
        )
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        raise StripeWebhookError("Invalid Stripe signature") from exc
