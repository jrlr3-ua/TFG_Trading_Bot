#!/bin/bash
# Parche para datasieve 0.1.9: renombra features_in → feature_list
# El bug está en pipeline.py línea 167: self.features_in debería ser self.feature_list
DATASIEVE_PATH=$(python3 -c "import datasieve; import os; print(os.path.dirname(datasieve.__file__))")
if [ -f "$DATASIEVE_PATH/pipeline.py" ]; then
    if grep -q "self.features_in" "$DATASIEVE_PATH/pipeline.py"; then
        sed -i 's/self\.features_in/self.feature_list/g' "$DATASIEVE_PATH/pipeline.py"
        echo "✅ datasieve parcheado: features_in → feature_list"
    else
        echo "✅ datasieve ya parcheado o sin bug"
    fi
fi
# Ejecutar freqtrade con todos los argumentos pasados
exec freqtrade "$@"
