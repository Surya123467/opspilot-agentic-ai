import json
from sqlalchemy import select
from app.db.models import AuditEvent, RunRecord
from app.db.session import SessionLocal

def create_run(thread_id, request):
    with SessionLocal() as db:
        db.add(RunRecord(thread_id=thread_id, request=request)); db.commit()

def update_run(thread_id, status, result=None):
    with SessionLocal() as db:
        row = db.scalar(select(RunRecord).where(RunRecord.thread_id == thread_id))
        if row:
            row.status = status
            row.result = json.dumps(result) if result is not None else None
            db.commit()

def add_event(thread_id, event_type, detail):
    with SessionLocal() as db:
        db.add(AuditEvent(thread_id=thread_id, event_type=event_type, detail=detail)); db.commit()

def get_events(thread_id):
    with SessionLocal() as db:
        rows = db.scalars(select(AuditEvent).where(AuditEvent.thread_id == thread_id).order_by(AuditEvent.id)).all()
        return [{"event_type": r.event_type, "detail": r.detail, "created_at": r.created_at.isoformat()} for r in rows]
