from pydantic import BaseModel, ConfigDict, Field, model_validator

from kj_atlas_api.models import DocumentV2


class GenerateNarrativeRequest(BaseModel):
    doc: DocumentV2
    narrativeTitle: str | None = None

    @model_validator(mode="after")
    def validate_reading_order(self) -> "GenerateNarrativeRequest":
        reading_order = self.doc.readingOrder or []
        card_ids = {card.id for card in self.doc.cards}
        island_ids = {island.id for island in self.doc.islands}
        known_ids = card_ids | island_ids

        if len(reading_order) == 0:
            raise ValueError("readingOrder must include at least one id")

        if len(reading_order) != len(set(reading_order)):
            raise ValueError("readingOrder must not include duplicate ids")

        unknown_ids = [entry_id for entry_id in reading_order if entry_id not in known_ids]
        if unknown_ids:
            raise ValueError("readingOrder includes unknown ids")

        return self


class LLMNarrativeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1)
    basedOnReadingOrder: list[str]
    warnings: list[str] | None = None


class GenerateNarrativeResponse(BaseModel):
    text: str
    basedOnReadingOrder: list[str]
    warnings: list[str] | None = None
