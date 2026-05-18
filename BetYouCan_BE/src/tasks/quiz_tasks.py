import logging
from datetime import datetime, timezone
import multiprocessing
from src.celery_app import celery_app
from src.helpers.db import SessionLocal
from src.models import goal_schemas, verifications_schemas  # adjust imports
from fastapi import HTTPException
from src.gpt.apicalls import generate_questions
import os
from src.models import auth_schemas  # ensure users table is registered
import asyncio
from sqlalchemy import or_



@celery_app.task(bind=True, max_retries=0, default_retry_delay=30)
def generate_quiz_for_goal(self, goal_id: str):
    db = SessionLocal() 
    claimed = False
    try:
        logging.info(
            "Quiz generation start goal=%s task=%s pid=%s proc=%s",
            goal_id,
            self.request.id,
            #self.request.hostname, #add when we have multiple hosts later
            os.getpid(),
            multiprocessing.current_process().name,
        )
        claim_result = (
            db.query(goal_schemas.Goal)
            .filter(goal_schemas.Goal.id == goal_id)
            .filter(
                or_(
                    goal_schemas.Goal.quiz_question_status.is_(None),
                    goal_schemas.Goal.quiz_question_status == "failed",
                )
            )
            .update({goal_schemas.Goal.quiz_question_status: "pending"})
        )
        db.commit()
        if claim_result == 0:
            logging.info("GoalID: %s already claimed or created", goal_id)
            return
        claimed = True

        goal = (
            db.query(goal_schemas.Goal)
            .filter(goal_schemas.Goal.id == goal_id)
            .first()
        )
        if not goal:
            logging.warning("Goal not found after claim: %s", goal_id)
            return

        QA_sets = asyncio.run(generate_questions(goal.user_input, goal.goal_type_id, db))
        questions_list = QA_sets["questions"]
        answers_list = QA_sets["answers"]
        
        # maybe add in check if questions and answers both have 5 questions. Zip may not be enough
        for question, answer in zip(questions_list, answers_list):
            new_QA_set_record = verifications_schemas.QuizQuestions(
                goal_id=goal_id,
                question=question,
                answer=answer,
            )
            db.add(new_QA_set_record)
        goal.quiz_question_status = "created"
        logging.info("Setting status=created for goal=%s", goal_id)
        db.commit()
        logging.info("Questions generated for GoalID: %s", goal_id)
    except Exception as e:
        # mark failed for visibility, then re-raise to trigger retry
        try:
            if claimed:
                goal = (
                    db.query(goal_schemas.Goal)
                    .filter(goal_schemas.Goal.id == goal_id)
                    .first()
                )
                if goal:
                    goal.quiz_question_status = "failed"
                    db.commit()
            self.retry()
        except Exception:
            db.rollback()
        raise
    finally:
        db.close()
