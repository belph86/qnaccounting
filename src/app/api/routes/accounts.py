from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_db
from src.app.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("")
async def get_accounts(
    sync: bool = Query(False, description="Sync accounts from bank before returning"),
    db: AsyncSession = Depends(get_db),
):
    """Get list of bank accounts. Optionally sync from Erste API first."""
    service = TransactionService(db)
    if sync:
        try:
            accounts = await service.sync_accounts()
        except RuntimeError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Failed to sync accounts: {e}")
    else:
        accounts = await service.get_local_accounts()

    return {
        "accounts": [
            {
                "id": acc.id,
                "account_number": acc.account_number,
                "iban": acc.iban,
                "currency": acc.currency,
                "name": acc.name,
                "balance": acc.balance,
                "is_active": acc.is_active,
            }
            for acc in accounts
        ]
    }


@router.get("/{account_id}/transactions")
async def get_transactions(
    account_id: str,
    sync: bool = Query(False, description="Sync transactions from bank before returning"),
    date_from: str | None = Query(None, description="Start date (ISO format)"),
    date_to: str | None = Query(None, description="End date (ISO format)"),
    db: AsyncSession = Depends(get_db),
):
    """Get transactions for a specific account. Optionally sync from Erste API first."""
    service = TransactionService(db)

    if sync:
        try:
            transactions = await service.sync_transactions(account_id, date_from, date_to)
        except RuntimeError as e:
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Failed to sync transactions: {e}")
    else:
        transactions = await service.get_local_transactions(account_id)

    return {
        "transactions": [
            {
                "id": tx.id,
                "account_id": tx.account_id,
                "amount": tx.amount,
                "currency": tx.currency,
                "direction": tx.direction,
                "status": tx.status,
                "variable_symbol": tx.variable_symbol,
                "specific_symbol": tx.specific_symbol,
                "constant_symbol": tx.constant_symbol,
                "counterparty_iban": tx.counterparty_iban,
                "counterparty_name": tx.counterparty_name,
                "description": tx.description,
                "booking_date": tx.booking_date.isoformat() if tx.booking_date else None,
                "value_date": tx.value_date.isoformat() if tx.value_date else None,
                "reference": tx.reference,
            }
            for tx in transactions
        ]
    }
