from sqlalchemy.orm import Session

from app.models import Agent, Revocation


def is_revoked(db: Session, agent_name):
    agent = (
        db.query(Agent)
        .filter(Agent.name == agent_name)
        .first()
    )

    if agent:
        return agent.revoked

    return False


def revoke_agent(db: Session, agent_name):
    agent = (
        db.query(Agent)
        .filter(Agent.name == agent_name)
        .first()
    )

    if not agent:
        agent = Agent(
            name=agent_name,
            public_key="pending",
            revoked=True
        )

        db.add(agent)

    else:
        agent.revoked = True

    db.add(
        Revocation(agent_name=agent_name)
    )

    db.commit()