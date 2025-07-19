import re

re_str = '^(?:\$|\d+|\/[^\/]*\/)$'
pattern = re.compile(re_str)

def test_addr_regex():
    """
    Test the addr-matching regex: should match only
    single '$', one or more digits, or '/.../' with no inner slashes.
    """
    positive = ["$", "0", "123", "/foo/", "//", "/$/", "/ssasdfe21efg.^$sefh342q/", '122331343311111']
    negative = ["/a/b/", "foo", "5,10", "", "/"]  # edge cases
    for s in positive:
        assert pattern.match(s), f"Expected to match valid addr '{s}'"
    for s in negative:
        assert not pattern.match(s), f"Expected NOT to match invalid addr '{s}'"

