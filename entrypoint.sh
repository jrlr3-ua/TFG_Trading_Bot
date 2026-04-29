#!/bin/bash
# Parche para datasieve 0.1.9 (aplicado en build-time via Dockerfile).
# Este entrypoint solo verifica que el parche persista en runtime.
DATASIEVE_PATH=$(python3 -c "import datasieve; import os; print(os.path.dirname(datasieve.__file__))")
if [ -f "$DATASIEVE_PATH/pipeline.py" ]; then
    if grep -q "self.features_in" "$DATASIEVE_PATH/pipeline.py"; then
        sed -i 's/self\.features_in/self.feature_list/g' "$DATASIEVE_PATH/pipeline.py"
        echo "datasieve parcheado en runtime: features_in -> feature_list"
    else
        echo "datasieve OK (parcheado en build-time)"
    fi
fi
exec freqtrade "$@"
