import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    account_id: Mapped[str] = mapped_column(String, ForeignKey("accounts.id"))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String, default="CZK")
    direction: Mapped[str] = mapped_column(String)  # INCOMING / OUTGOING
    status: Mapped[str] = mapped_column(String, default="Unmatched")  # Unmatched|Matched|Ignored|ManuallyMatched
    variable_symbol: Mapped[str | None] = mapped_column(String, nullable=True)
    specific_symbol: Mapped[str | None] = mapped_column(String, nullable=True)
    constant_symbol: Mapped[str | None] = mapped_column(String, nullable=True)
    counterparty_iban: Mapped[str | None] = mapped_column(String, nullable=True)
    counterparty_name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    booking_date: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    value_date: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    reference: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    account: Mapped["Account"] = relationship(back_populates="transactions")
