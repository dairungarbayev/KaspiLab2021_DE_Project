
import os
from typing import Type, Any

import pytest

from database.database import Database
from database.implementations.mysql_database import DatabaseMySQL

# using separate Database dbtest for testing

@pytest.fixture()
def connection_dict(request: Any) -> dict:
    return {"host": "localhost",
            "user": "root",
            "password": os.getenv("MYSQL_LOCAL_PASSWORD"),
            "database": "dbtest"
            }


@pytest.fixture(params=[DatabaseMySQL])
def database_implementation(request: Any) -> Type[Database]:
    implementation = request.param
    return implementation


@pytest.fixture()
def database_connected(
        request: Any,
        database_implementation: Type[Database],
        connection_dict: dict,
) -> Database:
    if database_implementation == DatabaseMySQL:
        return DatabaseMySQL(connection=connection_dict)
    return database_implementation()
