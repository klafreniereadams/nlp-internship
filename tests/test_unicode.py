def test_unicode_normalization_basic(cleaner):
    assert cleaner.normalize_unicode("ﬁ") == "fi"

def test_unicode_quotes(cleaner):
    assert cleaner.normalize_unicode("“hello”") == '"hello"'

def test_unicode_apostrophes(cleaner):
    assert cleaner.normalize_unicode("it’s") == "it's"

def test_unicode_dashes(cleaner):
    assert cleaner.normalize_unicode("a—b–c") == "a-b-c"

def test_unicode_whitespace(cleaner):
    assert cleaner.normalize_unicode("a\u00A0b") == "a b"

def test_unicode_non_string(cleaner):
    assert cleaner.normalize_unicode(None) is None
