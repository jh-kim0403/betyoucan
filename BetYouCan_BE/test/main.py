import asyncio
from src.gpt.apicalls import generate_questions
from src.helpers.db import SessionLocal

db = SessionLocal()

async def main():
    data = await generate_questions(
        user_input="Genesis 1",
        goal_type_id="ccf98a58-2dcc-44e2-8979-5cc9cb454a87",
        db=db
    )
    print(data)

asyncio.run(main())