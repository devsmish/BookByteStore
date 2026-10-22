"""Transaction hygiene, schema limits and upgrade paths, checked on a real database."""
from decimal import Decimal

import pymysql
import pytest

from app.db.purchases import PurchaseRepository
from app.exceptions import InvalidInputError


def test_unexpected_error_rolls_back_the_whole_purchase(make_session, monkeypatch, raw):
    seed = make_session()
    seed.admin.add_book("Neuromancer", "Gibson", Decimal("8.00"), 3)
    seed.auth.register("bob", "pw", Decimal("100.00"))

    s = make_session()
    bob = s.auth.login("bob", "pw")
    book = s.catalog.list_books()[0]

    def lock_timeout(self, *args, **kwargs):
        raise pymysql.err.OperationalError(1205, "Lock wait timeout exceeded; try restarting transaction")

    with monkeypatch.context() as patch:  # a local patch: the DB settings from the fixture must stay in place
        patch.setattr(PurchaseRepository, "add", lock_timeout)
        with pytest.raises(pymysql.err.OperationalError):
            s.purchase.purchase(bob.id, book.id, 2)

    # ANY later commit on the same connection must not persist the half-finished purchase
    s.purchase.top_up(bob.id, Decimal("1.00"))

    assert raw("SELECT stock FROM books WHERE id=%s", (book.id,))[0][0] == 3
    assert raw("SELECT balance FROM users WHERE id=%s", (bob.id,))[0][0] == Decimal("101.00")
    assert raw("SELECT COUNT(*) FROM purchases")[0][0] == 0


def test_top_up_beyond_the_column_limit_is_a_domain_error(make_session, raw):
    s = make_session()
    s.auth.register("rich", "pw", Decimal("99999990.00"))
    user_id = raw("SELECT id FROM users WHERE username='rich'")[0][0]

    with pytest.raises(InvalidInputError):
        s.purchase.top_up(user_id, Decimal("100.00"))

    assert raw("SELECT balance FROM users WHERE id=%s", (user_id,))[0][0] == Decimal("99999990.00")


@pytest.mark.parametrize("call", [
    lambda s: s.admin.add_book("T" * 300, "A", Decimal("1.00"), 1),
    lambda s: s.admin.add_book("T", "A" * 150, Decimal("1.00"), 1),
    lambda s: s.admin.add_book("T", "A", Decimal("100000000.00"), 1),
    lambda s: s.admin.add_book("T", "A", Decimal("1.00"), 10**12),
    lambda s: s.auth.register("u" * 150, "pw", Decimal("1.00")),
    lambda s: s.auth.register("u", "pw", Decimal("100000000.00")),
])
def test_values_that_do_not_fit_the_schema_are_domain_errors(make_session, call):
    with pytest.raises(InvalidInputError):
        call(make_session())


def test_importing_a_file_with_a_utf8_bom_does_not_store_the_bom(make_session, raw, tmp_path):
    path = tmp_path / "books.txt"
    path.write_bytes(b"\xef\xbb\xbfDune,Herbert,10.00,5\nNeuromancer,Gibson,8.00,3\n")

    make_session().admin.import_from_file(str(path))

    titles = [row[0] for row in raw("SELECT title FROM books ORDER BY id")]
    assert titles == ["Dune", "Neuromancer"]


def test_login_works_on_a_database_created_before_the_is_admin_column(make_session, raw):
    raw("ALTER TABLE users DROP COLUMN is_admin")  # emulate a schema from an older version

    make_session().auth.register("old", "pw", Decimal("1.00"))

    assert make_session().auth.login("old", "pw").username == "old"
