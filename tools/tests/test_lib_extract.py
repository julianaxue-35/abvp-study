import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from lib_extract import norm_title, find_cols, detect_year, fuzzy_matches


def test_norm_title_strips_nonalnum_and_lowercases():
    assert norm_title("Tag! You’re Home!  ") == "tagyourehome"


def test_find_cols_standard_infectious_layout():
    cols = find_cols(["Year", "First Author", "Journal", "Article Title", "Abstract", "Key Points"])
    assert cols["year"] == 0 and cols["author"] == 1 and cols["journal"] == 2
    assert cols["title"] == 3 and cols["abstract"] == 4 and cols["keypoints"] == 5


def test_find_cols_combined_author_journal():
    cols = find_cols([" ", "First Author, Journal", "Article Title", "Abstract"])
    assert cols["author"] == 1 and cols.get("combined_author_journal") is True
    assert cols["title"] == 2 and cols["abstract"] == 3


def test_find_cols_diplomate_layout():
    cols = find_cols(["Diplomate", "Journal", "Year", "Author", "Title", "Abstract"])
    assert cols["diplomate"] == 0 and cols["journal"] == 1 and cols["year"] == 2
    assert cols["author"] == 3 and cols["title"] == 4 and cols["abstract"] == 5


def test_detect_year_from_year_column():
    assert detect_year([2024.0, "x"], {"year": 0}) == 2024


def test_detect_year_scanned_from_text():
    assert detect_year(["2020/2021", "Animals"], {}) == 2020


def test_fuzzy_matches_flags_near_dup():
    got = fuzzy_matches("tagyourehomereunificationofpetcats",
                        ["tagyourehomereunificationofpetcat"], 0.80, 0.99)
    assert got and got[0][1] >= 0.80
