from typing import Protocol, TypedDict, Optional, List

class Question(TypedDict, total=False):
    qid: str
    title: str
    body: str
    author_id: str
    tags: List[str]
    created_at: int
    score: int
    answer_count: int

class QuestionRepo(Protocol):
    def create(self, q: Question) -> None: ...
    def get(self, qid: str) -> Optional[Question]: ...
