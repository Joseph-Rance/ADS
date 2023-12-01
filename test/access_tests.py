from ... import fynesse

import nose

def test_pp_data_not_empty():
    assert len(fynesse.access.sql_server.query_table("SELECT * FROM `pp_data` LIMIT 1")) == 1

def test_postcode_data_not_empty():
    assert len(fynesse.access.sql_server.query_table("SELECT * FROM `postcode_data` LIMIT 1")) == 1

nose.main("fynesse", defaultTest="fynesse/tests/access", argv=["", ""])