from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.utils import get_main_address
from app.models import Address

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)

    main_address = get_main_address()

    address = crud.get_address(session=session, address=main_address)
    if not address:
        address = Address(address=main_address, index=0)
        session.add(address)
        session.commit()

