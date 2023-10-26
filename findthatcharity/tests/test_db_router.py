from unittest.mock import Mock

from findthatcharity.db_router import DBRouter


def test_db_router__db_for_read__data_db():
    router = DBRouter()
    model = Mock(_meta=Mock(app_label="api"))
    assert router.db_for_read(model) == "data"
