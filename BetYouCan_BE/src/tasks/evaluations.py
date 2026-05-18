import logging
from src.helpers.bounty_ledger_utils import apply_bounty_ledger_entry
from src.celery_app import celery_app
from src.helpers.db import SessionLocal
from src.helpers.s3 import presign_get
from src.helpers.openai import evaluate_photo
from src.helpers.verification_utils import get_photo_verification_record, serp_image_search, hash_image, compare_image


@celery_app.task(bind=True, max_retries=0, default_retry_delay=20)
def evaluate_submission(self, submission_id: str):
    """
    Evaluate a user submission (photo/quiz answers).
    Call GPT here, update DB with results.
    """
    try:
        # 1) load submission + evidence from DB
        # 2) call GPT
        # 3) store result
        return {"submission_id": submission_id, "status": "ok"}
    except Exception as e:
        raise self.retry(exc=e)


@celery_app.task(bind=True, max_retries=0, default_retry_delay=20)
def evaluate_photo_verification(self, verification_id: str):
    """
    Evaluate a photo verification with GPT.
    """
    logging.info("evaluate_photo_verification started: %s", verification_id)
    db = SessionLocal()
    try:
        verification, photo, goal, goal_type = get_photo_verification_record(db, verification_id)

        goal_image_url = presign_get(photo.s3_key, expires_seconds=300)
        """
        serper_result = serp_image_search(goal_image_url)
        logging.info("Serper Result")
        logging.info(serper_result)
        exact_matches = serper_result.get("exact_matches")
        logging.info("Link: %s", exact_matches[0]["thumbnail"])
        
        if exact_matches and compare_image(hash_image(goal_image_url), hash_image(exact_matches[0]["thumbnail"])):
            logging.info("submitted image is an image taken from online")
            verification.result = "rejected"
            goal.verification_status = "failed"
            goal.status = "pending"
        else:
        
            logging.info("Submitting image to openai for evaluation")
            """
        result = evaluate_photo(prompt=goal_type.gpt_prompt, image_url=goal_image_url)
        if result.is_true:
            verification.result = "completed"
            goal.verification_status = "completed"
            goal.status = "resolved"
            apply_bounty_ledger_entry(goal.user_id, goal.id, "release", goal.bounty_amount, db)
        else:
            verification.result = "failed"
            goal.verification_status = "failed"
            goal.status = "resolved"
            apply_bounty_ledger_entry(goal.user_id, goal.id, "forfeit", goal.bounty_amount, db)
        meta = dict(photo.meta or {})
        meta["ai_check"] = {
            "is_true": result.is_true,
            "prob_true": result.prob_true,
            "prob_false": result.prob_false,
            "reason": result.reason,
        }
        photo.meta = meta
        db.commit()
        logging.info("Successfully evaluated photo for verification: %s", verification_id)
        return {"verification_id": verification_id, "result": verification.result}
    except Exception as e:
        logging.exception("Photo verification failed: %s", verification_id)
        db.rollback()
        raise self.retry(exc=e)
    finally:
        db.close()
