"""
TFG: Suite de Tests — Motor NLP (sentiment_ingestor.py v3.0)
============================================================
Valida los componentes críticos del pipeline NLP:
  - Test 3:  Limpieza de HTML (separación de tags pegados)
  - Test 3b: HTML complejo con tags anidados
  - Test 4:  NER — Detección de entidades per-coin
  - Test 4b: NER case-insensitive
  - Test 5:  Fallback de seguridad ante fallo de RSS
  - Test 5b: Completitud de alias NER

Ejecución: make test
"""
# Las dependencias pesadas ya están mockeadas por conftest.py
import data_engineering.sentiment_ingestor as NlpModule


def test_clean_html_logic():
    """
    Test 3: Asegura que el parseador HTML separe tags pegados
    evitando fundir palabras ("Bitcoinsoars" → "Bitcoin soars").
    """
    dirty_text = "<p>Bitcoin<b>soars</b> to $80k!</p>"
    clean_text = NlpModule.clean_html(dirty_text)

    assert "Bitcoin soars to $80k!" == clean_text
    assert "<b>" not in clean_text
    assert "<p>" not in clean_text


def test_clean_html_nested_tags():
    """
    Test 3b: HTML complejo con tags anidados y entidades.
    """
    dirty = "<div><span>Ethereum</span><em>upgrade</em>&amp;more</div>"
    clean = NlpModule.clean_html(dirty)

    assert "Ethereum" in clean
    assert "upgrade" in clean
    assert "<" not in clean


def test_detect_coins_ner():
    """
    Test 4: Verifica el pipeline de Named Entity Recognition (NER).
    Detecta criptomonedas por nombre y alias.
    """
    title_1 = "Ethereum and Cardano developers meet to discuss scaling."
    title_2 = "Cryptocurrency market drops 5% in massive sell-off."
    title_3 = "Vitalik announces new Ethereum roadmap"

    res_1 = NlpModule.detect_coins(title_1)
    res_2 = NlpModule.detect_coins(title_2)
    res_3 = NlpModule.detect_coins(title_3)

    assert "ETH" in res_1
    assert "ADA" in res_1
    assert len(res_2) == 0
    assert "ETH" in res_3


def test_detect_coins_case_insensitive():
    """
    Test 4b: La detección debe ser case-insensitive.
    """
    title = "BITCOIN hits new ATH while dogecoin lags behind"
    coins = NlpModule.detect_coins(title)

    assert "BTC" in coins
    assert "DOGE" in coins


def test_fallback_headlines():
    """
    Test 5: Validar que si todos los feeds RSS fallan,
    la app tiene titulares de fallback de seguridad.
    """
    assert len(NlpModule.FALLBACK_HEADLINES) > 0
    assert isinstance(NlpModule.FALLBACK_HEADLINES, list)
    has_bitcoin = any("Bitcoin" in h for h in NlpModule.FALLBACK_HEADLINES)
    assert has_bitcoin


def test_coin_aliases_completeness():
    """
    Test 5b: Validar que todos los pares del whitelist tienen alias NER.
    """
    expected_coins = ["BTC", "ETH", "SOL", "BNB", "ADA", "XRP",
                      "DOT", "LINK", "AVAX", "DOGE", "NEAR"]
    for coin in expected_coins:
        assert coin in NlpModule.COIN_ALIASES, f"Falta alias NER para {coin}"
        assert len(NlpModule.COIN_ALIASES[coin]) >= 2, \
            f"{coin} necesita al menos 2 alias para buena cobertura"
