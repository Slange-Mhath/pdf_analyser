import pytest
from main import get_pdf_list_from_sf_log, get_word_count, is_image, get_font_list, is_embedded, delete_junk_chars, clear_font_info
import json
import re


@pytest.fixture()
def test_sf_log():
    sf_log = "tests/test_files/dpms-sf.log"
    return sf_log


@pytest.fixture()
def test_pdf():
    pdf_file = "tests/test_files/24_words.pdf"
    return pdf_file


@pytest.fixture()
def test_image_pdf():
    image_pdf_file = "tests/test_files/pdf_1_0.pdf"
    return image_pdf_file


@pytest.fixture()
def list_of_fonts():
    list_of_fonts = [(11, 'ttf', 'TrueType', 'BCDFEE+DokChampa', 'F3', 'WinAnsiEncoding'),
                     (5, 'ttf', 'TrueType', 'BCDEEE+Calibri', 'F1', 'WinAnsiEncoding'),
                     (9, 'n/a', 'TrueType', 'TimesNewRomanPSMT', 'F2', 'WinAnsiEncoding')]
    return list_of_fonts


def test_get_pdf_list_from_sf_log(test_sf_log):
    pdf_list = get_pdf_list_from_sf_log(test_sf_log)
    assert len(pdf_list) == 25


def test_get_word_count(test_pdf):
    word_count = get_word_count(test_pdf)
    assert word_count == 24


def test_is_image(test_image_pdf, test_pdf):
    pdf_is_image = is_image(test_image_pdf)
    none_image_pdf = is_image(test_pdf)
    assert pdf_is_image is True
    assert none_image_pdf is not True


def test_get_font_list(test_image_pdf, test_pdf):
    font_list = get_font_list(test_pdf)
    fonts_as_str = []
    #check if the font list contains unique entries
    for font in font_list:
        fonts_as_str.append(json.dumps(font, sort_keys=True))
    assert len(set(fonts_as_str)) == len(font_list)
    assert len(font_list) == 3


def test_is_embedded(list_of_fonts):
    embedded_font = list_of_fonts[2]
    unembedded_font = list_of_fonts[1]
    assert is_embedded(embedded_font[3]) is True
    assert is_embedded(unembedded_font[3]) is False


def test_delete_junk_chars(list_of_fonts):
    for font in list_of_fonts:
        assert "+" not in delete_junk_chars(font[3])


def test_clear_font_info(list_of_fonts):
    cleared_fonts = []
    for font in list_of_fonts:
        cleared_fonts.append(clear_font_info(font))
    assert cleared_fonts[0] == {'font-name': 'DokChampa', 'font-no': 11, 'PostScript-type': 'TrueType', 'is_embedded': False}










