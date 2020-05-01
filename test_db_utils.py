from pytest import mark

from db_utils import trim_value


@mark.parametrize('val, expected', [
    ('foo"-"bar', 'foo"-"bar'),
    ('"foo-bar"', 'foo-bar'),
    ("'bar-foo'", 'bar-foo'),
])
def test_trim_value(val, expected):
    result = trim_value(val)
    assert result == expected
