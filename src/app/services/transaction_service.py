import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.account import Account
from src.app.models.transaction import Transaction
from src.app.services.erste_client import ErsteApiClient


class TransactionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.erste_client = ErsteApiClient(db)

    async def sync_accounts(self) -> list[Account]:
        """Fetch accounts from Erste API and store/update in local DB."""
        data = await self.erste_client.get_accounts()
        accounts = data.get("accounts", [])
        result = []

        for acc_data in accounts:
            acc_id = str(acc_data.get("id", ""))
            existing = await self.db.get(Account, acc_id)

            if existing:
                existing.account_number = acc_data.get("accountno", {}).get("number")
                existing.iban = acc_data.get("accountno", {}).get("cz-iban")
                existing.currency = acc_data.get("balance", {}).get("currency", "CZK")
                existing.name = acc_data.get("description")
                existing.balance = str(acc_data.get("balance", {}).get("value", ""))
                existing.updated_at = datetime.datetime.utcnow()
                result.append(existing)
            else:
                account = Account(
                    id=acc_id,
                    account_number=acc_data.get("accountno", {}).get("number"),
                    iban=acc_data.get("accountno", {}).get("cz-iban"),
                    currency=acc_data.get("balance", {}).get("currency", "CZK"),
                    name=acc_data.get("description"),
                    balance=str(acc_data.get("balance", {}).get("value", "")),
                )
                self.db.add(account)
                result.append(account)

        await self.db.commit()
        return result

    async def sync_transactions(self, account_id: str, date_from: str | None = None, date_to: str | None = None) -> list[Transaction]:
        """Fetch transactions from Erste API and store in local DB."""
        data = await self.erste_client.get_transactions(account_id, date_from, date_to)
        transactions = data.get("transactions", [])
        result = []

        for tx_data in transactions:
            tx_id = str(tx_data.get("id", ""))
            existing = await self.db.get(Transaction, tx_id)
            if existing:
                result.append(existing)
                continue

            amount_data = tx_data.get("amount", {})
            sender = tx_data.get("sender", {})
            receiver = tx_data.get("receiver", {})
            symbols = tx_data.get("symbols", {})

            # Determine direction
            amount_value = float(amount_data.get("value", 0))
            direction = "INCOMING" if amount_value > 0 else "OUTGOING"

            # Parse counterparty
            counterparty = receiver if direction == "OUTGOING" else sender
            counterparty_iban = counterparty.get("iban") or counterparty.get("accountno", {}).get("cz-iban")
            counterparty_name = counterparty.get("name")

            # Parse dates
            booking_date = None
            if tx_data.get("bookingDate"):
                try:
                    booking_date = datetime.datetime.fromisoformat(tx_data["bookingDate"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            value_date = None
            if tx_data.get("valuationDate"):
                try:
                    value_date = datetime.datetime.fromisoformat(tx_data["valuationDate"].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            transaction = Transaction(
                id=tx_id,
                account_id=account_id,
                amount=abs(amount_value),
                currency=amount_data.get("currency", "CZK"),
                direction=direction,
                variable_symbol=symbols.get("variableSymbol"),
                specific_symbol=symbols.get("specificSymbol"),
                constant_symbol=symbols.get("constantSymbol"),
                counterparty_iban=counterparty_iban,
                counterparty_name=counterparty_name,
                description=tx_data.get("description"),
                booking_date=booking_date,
                value_date=value_date,
                reference=tx_data.get("reference"),
            )
            self.db.add(transaction)
            result.append(transaction)

        await self.db.commit()
        return result

    async def get_local_accounts(self) -> list[Account]:
        """Get all accounts from local DB."""
        result = await self.db.execute(select(Account).order_by(Account.created_at))
        return list(result.scalars().all())

    async def get_local_transactions(self, account_id: str) -> list[Transaction]:
        """Get transactions for an account from local DB."""
        result = await self.db.execute(
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.booking_date.desc())
        )
        return list(result.scalars().all())
