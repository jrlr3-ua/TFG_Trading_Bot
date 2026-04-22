import pytest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Evitar dependencias que pesan gigabytes
sys.modules['transformers'] = MagicMock()
import data_engineering.sentiment_ingestor as NlpModule

def test_clean_html_logic():
    """
    Test 3: Asegura que el parseador HTML separe tags pegados
    evitando fundir palabras ("Bitcoinsoars").
    """
    dirty_text = "<p>Bitcoin<b>soars</b> to $80k!</p>"
    clean_text = NlpModule.clean_html(dirty_text)
    
    assert "Bitcoin soars to $80k!" == clean_text
    # Asegura que no queden rastros de tags
    assert "<b>" not in clean_text
    
def test_detect_coins_ner():
    """
    Test 4: Verifica el pipeline de Named Entity Recognition (NER).
    """
    title_1 = "Ethereum and Cardano developers meet to discuss scaling."
    title_2 = "Cryptocurrency market drops 5% in massive sell-off."
    
    res_1 = NlpModule.detect_coins(title_1)
    res_2 = NlpModule.detect_coins(title_2)
    
    assert "ETH" in res_1
    assert "ADA" in res_1
    # Cuando no hay mención, no debe detectar nada
    assert len(res_2) == 0

def test_fallback_logic():
    """
    Test 5: Validar que si hay 0 feeds de RSS vivos (falla DNS, etc)
    la app tenga fallback de seguridad.
    """
    # En el archivo está mapeado a FALLBACK_HEADLINES
    assert len(NlpModule.FALLBACK_HEADLINES) > 0
    assert "Bitcoin" in NlpModule.FALLBACK_HEADLINES[0]
