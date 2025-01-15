from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, DateTime
from worker.utils import tools
from datetime import datetime
from worker.utils.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=tools.get_uuid)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, default="client")

    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=tools.get_dt
    )
    last_online: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=tools.get_dt
    )
