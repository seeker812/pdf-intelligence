import uuid

from sqlalchemy.orm import Session

from backend.app.api.v1.models.entities.document_insight_entity import DocumentInsightEntity


class InsightRepository:
    def save_insights(
        self,
        db: Session,
        document_id: str,
        insights: list[str],
    ) -> list[DocumentInsightEntity]:
        entities: list[DocumentInsightEntity] = []

        for insight in insights:
            entity = DocumentInsightEntity(
                id=str(uuid.uuid4()),
                document_id=document_id,
                insight=insight,
            )
            entities.append(entity)

        db.add_all(entities)
        db.commit()

        return entities

    def get_insights(self, db: Session, document_id: str) -> list[DocumentInsightEntity]:
        return (
            db.query(DocumentInsightEntity)
            .filter(DocumentInsightEntity.document_id == document_id)
            .all()
        )
