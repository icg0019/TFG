import pandas as pd
import pytest
import numpy as np
from ..algoritmo.necesidades import Necesidades

# Datos de prueba
df_prueba_1 = pd.DataFrame({
    'MATNR': [51, 24, 35],
    'REFERENCIA': ['P51', 'P24', 'P35'],
    'C1': ['Rojo', 'Azul', 'Verde'],
    'C2': ['Verde', 'Rojo', 'Rojo'],
    'Necesidades_min': [24500, 35487, 10024],
    'Necesidades_max': [85742, 600000, 45246]
})

datos_esperados_1 = {
    '0': [1, 0, 1],
    '1': [0, 1, 0],
    '2': [1, 0, 1]
}
compatibilidades_esperados_1  = pd.DataFrame(datos_esperados_1)

df_necesidades_1 = pd.DataFrame({
    'MATNR': [51, 24, 35],
    'REFERENCIA': ['P51', 'P24', 'P35'],
    'C1': ['Rojo', 'Azul', 'Verde'],
    'C2': ['Verde', 'Rojo', 'Rojo'],
    'Tramos_minimos': [2, 3, 1],
    'Tramos_maximos': [85742, 600000, 45246]
})


df_prueba_2 =pd.DataFrame({
    'MATNR': [51, 24, 35],
    'REFERENCIA': ['P51', 'P24', 'P35'],
    'C1': ['Rojo', None, 'Verde'],
    'C2': ['Verde', 'Rojo', 'Rojo'],
    'Necesidades_min': [24500, 35487, 10024],
    'Necesidades_max': [85742, 600000, 45246]
})

datos_esperados_2 = {
    '0': [1, 1, 1],
    '1': [1, 1, 1],
    '2': [1, 1, 1]
}
compatibilidades_esperados_2 = pd.DataFrame(datos_esperados_2)

# Función para probar creacion de compatibilidades
@pytest.mark.parametrize("df_prueba, df_esperado", [
    (df_prueba_1, compatibilidades_esperados_1 ),
    (df_prueba_2, compatibilidades_esperados_2 ),
])
def test_compatibilidades(df_prueba, df_esperado):
    necesidades = Necesidades(df_prueba)
    compatibilidades = necesidades.compatibilidad_productos_df()
    assert np.array_equal(compatibilidades.values, df_esperado.values), "Los valores de los DataFrames no son iguales"
    
    
    
# Función para probar creacion de Necesidades
@pytest.mark.parametrize("df_prueba, df_esperado", [
    (df_prueba_1, compatibilidades_esperados_1 ),
    (df_prueba_2, compatibilidades_esperados_2 ),
])
def test_crear_conjunto_productos(df_prueba, df_esperado):
    necesidades = Necesidades(df_prueba)
    compatibilidades = necesidades.compatibilidad_productos_df()
    assert np.array_equal(compatibilidades.values, df_esperado.values), "Los valores de los DataFrames no son iguales"