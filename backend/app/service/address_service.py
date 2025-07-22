from app import crud

from sqlmodel import Session

from app.models import Address


def create_address_job(session: Session, job_data):
    return crud.create_address_job(session=session, job_data=job_data)

def get_addresses(session: Session):
    return crud.get_addresses(session=session)

def check_address_exists(*, session: Session, address: str) -> bool:
    return crud.check_address_exists(session=session, address=address)

def get_address(session: Session, address: str) -> Address:
    return crud.get_address(session=session, address=address)