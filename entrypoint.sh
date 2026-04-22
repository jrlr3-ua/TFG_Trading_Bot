#!/bin/bash
# Parche quirÃºrgico para datasieve 0.1.9:
# El bug estÃ¡ en pipeline.py - usa 'features_in' que no existe.
# Lo correcto es 'feature_list'. Pero SOLO debemos parchear las
# referencias en _validate_arguments (lÃ­neas 155, 160, 167, 168, 170),
# NO la asignaciÃ³n 'self.feature_list = ...' de la lÃ­nea 154.
DATASIEVE_PATH=$(python3 -c "import datasieve; import os; print(os.path.dirname(datasieve.__file__))")
if [ -f "$DATASIEVE_PATH/pipeline.py" ]; then
    if grep -q "self.features_in" "$DATASIEVE_PATH/pipeline.py"; then
        sed -i 's/self\.features_in/self.feature_list/g' "$DATASIEVE_PATH/pipeline.py"
        echo "datasieve parcheado: features_in -> feature_list"
    else
        echo "datasieve ya parcheado o sin bug"
    fi
fi
exec freqtrade "$@"
