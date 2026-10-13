from sqlalchemy import text

def test_database_connection(db_connection):
    database_name = db_connection.execute(
        text("SELECT current_database()")
    ).scalar_one()

    assert database_name == "kijflow_test"