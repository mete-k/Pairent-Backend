from ports.question_repo import QuestionRepo, Question
from adaptors.nulls import IdGen, Clock

class ForumService:
    def __init__(self, questions: QuestionRepo, idgen: IdGen, clock: Clock):
        self.questions = questions
        self.idgen = idgen
        self.clock = clock

    def create_question(self, *, author_id: str, title: str, body: str = "", tags: list[str] | None = None) -> dict:
        if not title or len(title.strip()) < 3:
            raise ValueError("title must be at least 3 characters")

        qid = self.idgen.new_id()
        q: Question = {
            "qid": qid,
            "title": title.strip(),
            "body": (body or "").strip(),
            "author_id": author_id,
            "tags": tags or [],
            "created_at": self.clock.now_ts(),
            "score": 0,
            "answer_count": 0,
        }
        self.questions.create(q)
        return {"qid": qid}
    def get_question(self, qid: str) -> dict:
        q = self.questions.get(qid)
        if not q:
            raise ValueError("question not found")
        return q