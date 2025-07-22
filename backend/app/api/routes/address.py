from typing import Any

from fastapi import APIRouter, HTTPException, status


from app.models import AddressCreationJob
from app.api.models.models import *
from app.api.deps import SessionDep
from app.service import address_service as service

router = APIRouter(prefix="/address", tags=["address"])

@router.post("", response_model=ResponseModel[AddressCreationJob], status_code=status.HTTP_201_CREATED)
def create_addresses(session: SessionDep, create_address_request: CreateAddressJobRequest) -> Any:
    try:
        job = service.create_address_job(session=session, job_data=create_address_request)
        return ResponseModel(status="success", data=job, message="Job created successfully")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job creation failed")

@router.get("", response_model=ResponseModel[list[AddressResponse]], status_code=status.HTTP_200_OK)
def get_addresses(session: SessionDep) -> Any:
    try:
        addresses = service.get_addresses(session=session)
        return ResponseModel(data=addresses, status="success", message="Addresses retrieved successfully")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to retrieve addresses")
