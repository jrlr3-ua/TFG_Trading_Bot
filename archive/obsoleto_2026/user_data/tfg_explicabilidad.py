import pandas as pd
import pandas_ta as ta
import numpy as np
import lightgbm as lgb
import matplotlib.pyplot as plt
import os
import glob
import warnings

# Si no está instalado shap, usar feature importance de lightgbm
try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
    print("Módulo 'shap' no encontrado. Usa 'pip install shap' para gráficos avanzados.")

warnings.filterwarnings('ignore')

print("📊 [TFG] EXTRACTOR DE EXPLICABILIDAD (FEATURE IMPORTANCE)")
print("─" * 60)

# Cargar datos BTC
data_path = "/freqtrade/user_data/data/binance/futures/BTC_USDT_USDT-5m-futures.feather"
if not os.path.exists(data_path):
    print(f"Error: No se encuentra {data_path}")
    exit(1)

print("1. Cargando datos reales de Binance (BTC/USDT)...")
df = pd.read_feather(data_path)
df.columns = ["date", "open", "high", "low", "close", "volume"]

# Replicar Feature Engineering v2.1
print("2. Recreando Feature Engineering (12 Features)...")
df['rsi'] = ta.rsi(df['close'], length=14)
df['mfi'] = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14)
stoch = ta.stochrsi(df['close'], length=14)
if stoch is not None and not stoch.empty:
    df['stoch_rsi'] = stoch.iloc[:, 0]
else:
    df['stoch_rsi'] = 0

macd = ta.macd(df['close'])
if macd is not None and not macd.empty:
    df['macd_hist'] = macd.iloc[:, 1]
else:
    df['macd_hist'] = 0

bb = ta.bbands(df['close'])
if bb is not None and not bb.empty:
    df['bb_width'] = bb.iloc[:, 2] # Bandwidth
else:
    df['bb_width'] = 0

df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
df['obv'] = ta.obv(df['close'], df['volume'])
df['log_return'] = np.log(df['close'] / df['close'].shift(1))
df['return_std'] = df['log_return'].rolling(20).std()
df['volume_sma'] = df['volume'].rolling(50).mean()
df['candle_dir'] = np.where(df['close'] > df['open'], 1, -1)

# Sentimiento mockeado para el plot (ya que FinBERT está en Postgres)
df['sentiment_nlp'] = np.random.normal(0, 0.3, len(df))

# Target Regresión FreqAI
df['target_price_change'] = (df['close'].shift(-20) - df['close']) / df['close']

# Limpiar nulos
df = df.dropna()

features = [
    'rsi', 'mfi', 'stoch_rsi', 'macd_hist', 'bb_width', 
    'atr', 'obv', 'log_return', 'return_std', 'volume_sma',
    'candle_dir', 'sentiment_nlp'
]

X = df[features]
y = df['target_price_change']

print(f"   ► Muestras preparadas: {len(X)}")

# Entrenamiento
print("3. Entrenando LightGBM (TFG Model)...")
model = lgb.LGBMRegressor(
    n_estimators=100,
    learning_rate=0.05,
    random_state=42,
    verbose=-1
)
model.fit(X, y)

# Extracción Importancia nativa
print("\n🏆 RANKING DE FEATURE IMPORTANCE (LightGBM NATIVO)")
print("─" * 60)
importance = model.feature_importances_
feature_imp = pd.DataFrame(sorted(zip(importance, features)), columns=['Value','Feature'])
for i, row in feature_imp.sort_values(by="Value", ascending=False).iterrows():
    print(f"   {row['Feature']:<15} | Importancia: {row['Value']:.2f}")

# Plot Nativo
plt.figure(figsize=(10, 6))
plt.barh(feature_imp['Feature'], feature_imp['Value'], color='teal')
plt.title('Feature Importance (LightGBM) - TFG Trading Bot')
plt.xlabel('Importancia (Número de particiones en árboles)')
plt.tight_layout()
os.makedirs('/freqtrade/user_data/plots', exist_ok=True)
plt.savefig('/freqtrade/user_data/plots/lgbm_importance.png', dpi=300)
print("\n✅ Gráfico 1 guardado: user_data/plots/lgbm_importance.png")

# SHAP EXPLAINABILITY
if HAS_SHAP:
    print("\n🔍 4. Calculando Explicabilidad con SHAP Values...")
    explainer = shap.TreeExplainer(model)
    # limitamos a 5000 para no reventar la RAM
    shap_values = explainer.shap_values(X.sample(min(5000, len(X)), random_state=42))
    
    plt.figure()
    shap.summary_plot(shap_values, X.sample(min(5000, len(X)), random_state=42), show=False)
    plt.title('SHAP Summary - Impacto de Variables en la IA')
    plt.tight_layout()
    plt.savefig('/freqtrade/user_data/plots/shap_summary.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfico 2 guardado: user_data/plots/shap_summary.png")
else:
    print("\n💡 Para obtener el gráfico académico SHAP, instala la librería:")
    print("   pip install shap")
    print("   Y vuelve a correr este script.")

print("─" * 60)
print("🎯 Todo listo para copiar a la memoria del TFG.")
