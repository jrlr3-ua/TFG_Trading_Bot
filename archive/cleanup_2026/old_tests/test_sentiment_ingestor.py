"""
Tests Unitarios v3.0 — Motor NLP (FinBERT + NER)
=================================================
Suite de tests para validar:
1. Limpieza HTML de feeds RSS
2. Extracción de titulares con feedparser
3. Análisis de sentimiento con FinBERT (mock)
4. NER: Detección de criptomonedas en titulares (NUEVO v3.0)
5. Sentimiento per-coin: Asignación correcta de score por moneda (NUEVO v3.0)
"""

import pytest
from unittest.mock import MagicMock, patch
from data_engineering.sentiment_ingestor import (
    clean_html, fetch_headlines, analyze_sentiment, detect_coins, save_coin_sentiment
)


def test_clean_html():
    """Valida la limpieza correcta de las basurillas HTML del RSS feed."""
    dirty = "<p>Bitcoin <b>soars</b> to $80k!</p>"
    clean = clean_html(dirty)
    assert clean == "Bitcoin soars to $80k!", "Should completely strip out HTML logic."


@patch('data_engineering.sentiment_ingestor.feedparser')
def test_fetch_headlines_valid_rss(mock_feedparser):
    """Prueba que el extractor coge bien los títulos y salta los vacíos."""
    mock_feed = MagicMock()
    mock_feed.bozo = False
    mock_feed.entries = [
        {"title": "Ethereum upgrade brings massive changes"},
        {"title": "Tiny"}, # Menos de 10 caracteres (será filtrado)
    ]
    mock_feedparser.parse.return_value = mock_feed
    
    # Run Function
    headlines = fetch_headlines()
    
    # Assertions
    assert len(headlines) > 0
    # Como simulamos feedparser, todas las 3 fuentes retornarán "Ethereum..."
    # Y filtrará "Tiny"
    assert any("Ethereum" in h["title"] for h in headlines)


def test_analyze_sentiment_logic():
    """Verifica que procesa correctamente la respuesta de HuggingFace FinBERT."""
    # Mocking classifier output
    def mock_classifier(titles, truncation=True):
        return [
            {"label": "positive", "score": 0.95},
            {"label": "negative", "score": 0.80},
            {"label": "neutral", "score": 0.99}
        ]
    
    mock_headlines = [
        {"title": "Bullish!", "source": "fake"},
        {"title": "Bearish!", "source": "fake"},
        {"title": "Flat", "source": "fake"}
    ]
    
    results = analyze_sentiment(mock_classifier, mock_headlines)
    
    assert len(results) == 3
    # Check Positive mapping (+1)
    assert results[0]["sentiment_score"] == 0.95
    # Check Negative mapping (-1)
    assert results[1]["sentiment_score"] == -0.80
    # Check Neutral mapping (0)
    assert results[2]["sentiment_score"] == 0


# ═══════════════════════════════════════════════════════════════════
# TESTS v3.0: Named Entity Recognition (NER) para criptomonedas
# ═══════════════════════════════════════════════════════════════════

def test_detect_coins_single():
    """NER: Detecta una sola criptomoneda en un titular."""
    assert detect_coins("Bitcoin breaks resistance levels") == ["BTC"]
    assert detect_coins("Ethereum fees drop significantly") == ["ETH"]
    assert detect_coins("Solana reaches new ATH") == ["SOL"]


def test_detect_coins_multiple():
    """NER: Detecta múltiples criptomonedas en un titular."""
    coins = detect_coins("Bitcoin and Ethereum surge while Solana drops")
    assert "BTC" in coins
    assert "ETH" in coins
    assert "SOL" in coins
    assert len(coins) == 3


def test_detect_coins_aliases():
    """NER: Detecta criptomonedas por alias (no solo por ticker)."""
    assert detect_coins("Vitalik announces new Ether update") == ["ETH"]
    assert detect_coins("Ripple wins SEC lawsuit") == ["XRP"]
    assert detect_coins("Dogecoin pumps after Elon tweet") == ["DOGE"]
    assert detect_coins("Cardano smart contracts go live") == ["ADA"]


def test_detect_coins_none():
    """NER: No detecta monedas en titulares genéricos."""
    assert detect_coins("Crypto market drops 5% today") == []
    assert detect_coins("SEC announces new regulations") == []


def test_detect_coins_no_false_positive():
    """NER: No produce falsos positivos con palabras similares."""
    # "link" dentro de "hyperlink" NO debería detectar LINK/Chainlink
    result = detect_coins("Click this hyperlink for details")
    assert "LINK" not in result


def test_detect_coins_case_insensitive():
    """NER: La detección es case-insensitive."""
    assert detect_coins("BITCOIN is king") == ["BTC"]
    assert detect_coins("bitcoin is king") == ["BTC"]
    assert detect_coins("Bitcoin is king") == ["BTC"]
