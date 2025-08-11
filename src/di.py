from adaptors.nulls import Uuid4Gen, SystemClock
from adaptors.local.question_repo_mem import QuestionRepoMem
from service.forum_service import ForumService

def build_forum_service_local() -> ForumService:
    return ForumService(
        questions=QuestionRepoMem(),
        idgen=Uuid4Gen(),
        clock=SystemClock(),
    )
