def test_expand_br(cleaner):
    assert cleaner.expand_abbreviations("3 br") == "3 bedroom"

def test_expand_ba(cleaner):
    assert cleaner.expand_abbreviations("2 ba") == "2 bathroom"

def test_expand_w_slash(cleaner):
    assert cleaner.expand_abbreviations("w/ garage") == "with garage"

def test_expand_w_o(cleaner):
    assert cleaner.expand_abbreviations("w/o garage") == "without garage"

def test_expand_mbr(cleaner):
    assert cleaner.expand_abbreviations("mbr suite") == "master bedroom suite"

def test_expand_case_insensitive(cleaner):
    assert cleaner.expand_abbreviations("BR") == "bedroom"
