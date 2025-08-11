from typing import Optional
from ports.question_repo import QuestionRepo, Question

class QuestionRepoMem(QuestionRepo):
    def __init__(self):
        self.items: dict[str, Question] = {}

    def create(self, q: Question) -> None:
        self.items[q["qid"]] = q

    def get(self, qid: str) -> Optional[Question]:
        return self.items.get(qid)
