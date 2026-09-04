"""Turkce yazim motoru regresyon testleri.

Buradaki her vaka gercekten uretilmis bir hatadan geliyor. Motor degistirilirse
bu testler eski hatalarin geri gelmesini engeller.
"""
import pytest
from tr_fix import fix_text, fix_word


@pytest.mark.parametrize("ascii_in,expected", [
    # temel kok + ek uyumu
    ("musteri", "müşteri"),
    ("kullanicilarin", "kullanıcıların"),
    ("islemlerini", "işlemlerini"),
    ("goruntulemesi", "görüntülemesi"),
    ("odeme adiminda", "ödeme adımında"),
])
def test_basic_roots(ascii_in, expected):
    assert fix_text(ascii_in) == expected


@pytest.mark.parametrize("ascii_in,expected", [
    # -abil- yeterlilik eki unlu uyumuna GIRMEZ: durdurabileyim, durdurabılayım degil
    ("durdurabileyim", "durdurabileyim"),
    ("alabileyim", "alabileyim"),
    ("tiklayabilsin", "tıklayabilsin"),
    ("tekrarlanabilir", "tekrarlanabilir"),
    ("kapatilabilsin", "kapatılabilsin"),
])
def test_abil_suffix_does_not_harmonise(ascii_in, expected):
    assert fix_text(ascii_in) == expected


@pytest.mark.parametrize("ascii_in,expected", [
    # -ken eki sabittir: yaparken, yaparkan degil
    ("yaparken", "yaparken"),
    ("bakarken", "bakarken"),
    ("olustururken", "oluştururken"),
    ("varken", "varken"),
    ("yokken", "yokken"),
    ("cevrimdisiyken", "çevrimdışıyken"),
])
def test_ken_suffix_is_fixed(ascii_in, expected):
    assert fix_text(ascii_in) == expected


@pytest.mark.parametrize("ascii_in,expected", [
    # et-/ed- yardimci fiili de uyuma girmez
    ("kaydedip", "kaydedip"),
    ("kaydedilmeli", "kaydedilmeli"),
    ("teyit edildikten", "teyit edildikten"),
])
def test_auxiliary_et_does_not_harmonise(ascii_in, expected):
    assert fix_text(ascii_in) == expected


@pytest.mark.parametrize("ascii_in,expected", [
    # ek icindeki unsuz kurallari
    ("olusturuldugunda", "oluşturulduğunda"),   # g -> g yumusak, unluler arasi
    ("gorusme", "görüşme"),                     # s -> s sapkali
    ("yapilmistir", "yapılmıştır"),
    ("acikca", "açıkça"),                       # sert unsuz sonrasi c -> c
    ("zorlamadikca", "zorlamadıkça"),
    ("guvenligi", "güvenliği"),                 # kok unluyle bitince ek basi g -> g
])
def test_consonant_rules_in_suffix(ascii_in, expected):
    assert fix_text(ascii_in) == expected


@pytest.mark.parametrize("ascii_in,expected", [
    # ince ek alan istisnalar: saat, rol, kontrol, kabul, ihlal
    ("saatleri", "saatleri"),        # saatlari DEGIL
    ("saatlerine", "saatlerine"),
    ("kontrolu", "kontrolü"),
    ("rolu", "rolü"),
    ("kabulde", "kabulde"),          # kabulda DEGIL
    ("ihlali", "ihlali"),            # ihlali, ihlali DEGIL
])
def test_front_harmony_exceptions(ascii_in, expected):
    assert fix_text(ascii_in) == expected


@pytest.mark.parametrize("ascii_in,expected", [
    # kok cakismasi: uzun eslesme her zaman dogru degil
    ("gecen", "geçen"),          # "gece" koku kapmamali
    ("gecerken", "geçerken"),
    ("gece", "gece"),
    ("istenir", "istenir"),      # "isten" (isten ayrilmak) kapmamali
    ("analiziyle", "analiziyle"),# "ana" koku kapmamali
    ("bastiginda", "bastığında"),# "bas" degil "bas" (basmak)
    ("android", "Android"),
])
def test_root_collisions(ascii_in, expected):
    assert fix_text(ascii_in) == expected


def test_technical_terms_are_left_alone():
    """Teknik terimler ve kisaltmalar bozulmamali."""
    text = "asciifolding filtresi API uzerinden SMS ve OTP ile SCIM"
    out = fix_text(text)
    for term in ("asciifolding", "API", "SMS", "OTP", "SCIM"):
        assert term in out, f"{term} bozuldu: {out}"


def test_placeholders_are_preserved():
    """{placeholder} icerigi sablon degiskeni, kelime degil."""
    out = fix_text("{persona} {surface} uzerinde {obj} guncellenir")
    assert "{persona}" in out and "{surface}" in out and "{obj}" in out
    assert "güncellenir" in out


def test_capital_i_becomes_dotted():
    assert fix_word("Islem") == "İşlem"
    assert fix_word("Istek") == "İstek"


def test_idempotent():
    """Duzeltilmis metin tekrar islenince degismemeli."""
    once = fix_text("kullanici odeme adiminda hata aliyor")
    assert fix_text(once) == once
