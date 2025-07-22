from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.service import transaction_service as service
from app.api.models.models import *

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=ResponseModel[TransactionResponse], response_model_exclude_none=True)
def create_transaction(session: SessionDep, transaction_request: CreateTransactionRequest):
    try:
        tx = service.create_transaction(session=session, request=transaction_request)
        return ResponseModel(data=tx, status="success", message="Transaction created successfully")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/history", response_model=ResponseModel[list[TransactionHistoryResponse]], status_code=status.HTTP_200_OK)
def get_transactions_history_by_address(session: SessionDep, address: str):
    try:
        transactions = service.get_transactions_history_by_address(session=session, address=address)
        return ResponseModel(data=transactions, status="success", message="Transaction history retrieved successfully")
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address history not found.")

@router.post("/validate", status_code=status.HTTP_200_OK)
def validate_transaction(session: SessionDep, transaction_hash: ValidateTransactionRequest):
    try:
        transactions = service.validate_transaction_hash(session=session, transaction_hash=transaction_hash.transaction_hash)
        return ResponseModel(data=transactions, status="success", message="Transaction validated and history retrieved successfully")
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Couldn't validate the transaction.")

