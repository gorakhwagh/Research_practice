from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=500)
    run_id: UUID = Field(default_factory=uuid4)

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_blank(cls, value: str) -> str:
        topic = value.strip()
        if not topic:
            raise ValueError("Research topic must not be blank.")
        return topic


class ResearchResponse(BaseModel):
    run_id: UUID
    report: str
