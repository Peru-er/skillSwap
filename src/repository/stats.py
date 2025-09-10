
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database.models import Skill, Exchange, User  # перевір, чи такі моделі є

def get_top_skills(db: Session):
    return (
        db.query(Skill.name, func.count(Skill.id).label('count'))
        .join(Exchange, Exchange.skill_id == Skill.id)
        .group_by(Skill.id)
        .order_by(func.count(Skill.id).desc())
        .limit(10)
        .all()
    )

def get_active_users(db: Session):
    return (
        db.query(User.username, func.count(Exchange.id).label('exchanges'))
        .join(Exchange, Exchange.user_id == User.id)
        .group_by(User.id)
        .order_by(func.count(Exchange.id).desc())
        .limit(10)
        .all()
    )

def get_exchange_success_rate(db: Session):
    total = db.query(func.count(Exchange.id)).scalar()
    success = db.query(func.count(Exchange.id)).filter(Exchange.status == 'success').scalar()
    if total == 0:
        return {'success_rate': 0}
    return {'success_rate': round((success / total) * 100, 2)}

