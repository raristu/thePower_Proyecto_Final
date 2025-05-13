'''Este archivo contiene las funciones que se utilizan en los archivos principales del proyecto'''

# Importamos las librerías necesarias
import pandas as pd
import numpy as np
from datetime import datetime
import os


# Configuración para mostrar todas las columnas
pd.set_option('display.max_columns', None)

# 1. PREANÁLISIS --------------------------------------------------------------------

# Nulos por columnas
def nulos_col(df):
    """Esta función calcula los nulos de todas las columnas.

    Args:
        df (pd.Dataframe): dataframe del que queremos obtener los valores nulos.
    
    Returns: dataframe con los valores nulos de cada columna.
    """    
    nulos = df.isnull().sum()
    porcentaje_nulos = round(df.isnull().sum()/df.shape[0]*100,2)
    df_nulos = pd.DataFrame({"Valores_nulos": nulos,
                            "Porcentaje_nulos": porcentaje_nulos})
    df_nulos = df_nulos[df_nulos['Valores_nulos'] > 0]
    if len(df_nulos['Valores_nulos']) == 0:
        print("No hay valores nulos")
        print('-'*50)
    else:
        print("Los nulos por columna se distribuyen de la siguiente forma:")
        display(df_nulos)
        print('-'*50)

# Frecuencias de los valores de las variables categóricas
def frec_cat(df):
    """Esta función obtiene las frecuencias de los valores de las variables categóricas de un Dataframe.

    Args:
        df (pd.Dataframe): dataframe del que queremos obtener las frecuencias.
    
    Returns: frecuencias de los valores.
    """   
    print('La distribución de frecuencias de las variables categóricas es:\n')
    df_cat = df.select_dtypes(include ='O')
    for col in df_cat.columns:
        frec = df_cat[col].value_counts()
        porc = round(frec/df_cat.shape[0]*100,2)
        df_aux = pd.DataFrame({'Frecuencia' : frec,
                               'Porcentaje' : porc})
        print(f'Para la columna {col.upper()}, los valores únicos son:')
        print(df[col].unique())
        display(df_aux)
        print ('-'*50)  

# Función para realizar un preanálisis
def preanalisis(df):
    """Esta función realiza un preanálisis de los datos, mostrando:
        - Cantidad de filas y columnas
        - Valores duplicados
        - Valores nulos
        - Estadísticos descriptivos de las variables numéricas y categóricas
        - La distribución de frecuencias de las variables categóricas

    Args:
        df (pd.Dataframe): dataframe a analizar.

    Returns: información del dataframe.
    """    
    print(f'El dataframe tiene {df.shape[0]} filas y {df.shape[1]} columnas')
    print('-'*50)
    print(f'Tenemos un total de {df.duplicated().sum()} valores duplicados')
    print('-'*50)
    display(df.info())
    print('-'*50)
    nulos_col(df)
    print('Los estadísticos descriptivos de las variables numéricas son:')
    display(df.describe().T)
    print('-'*50)
    num_categoricas = df.select_dtypes(include=['O']).shape[1]
    if num_categoricas == 0:
        print("No hay variables categóricas")
    else:    
        print('Los estadísticos descriptivos de las variables categóricas son:')
        display(df.describe(include='O').T)
        print('-'*50)
        frec_cat(df)     

# 2. LIMPIEZA INICIAL --------------------------------------------------------------

# Función para homogeneizar el nombre de las columnas

def homogeneizar_nombre_columnas(df):
    """Esta función homogeneiza los nombres de las columnas:
        - Elimina espacios al principio y al final
        - Añade un guión bajo entre palabras
        - Reemplaza caracteres especiales por guiones bajos
        - Reemplaza múltiples guiones bajos por uno solo
        - Elimina guiones bajos al principio y al final
        - Pone todo en minúsculas
        - Pone la primera letra de cada palabra en mayúsculas

    Args:
        df (pd.Dataframe): dataframe a homogeneizar.

    Returns: dataframe modificado con los nombres de las columnas homogeneizadas.
    """  
    df.columns = (df.columns
                            .str.strip() # Elimina espacios al principio y al final
                            .str.replace(r"([a-z])([A-Z])", r"\1_\2", regex=True) # Añade un guión bajo entre palabras
                            .str.replace(r"[^a-zA-Z0-9]", "_", regex=True)  # Reemplaza caracteres especiales por guiones bajos
                            .str.replace(r"_+", "_", regex=True) # Reemplaza múltiples guiones bajos por uno solo
                            .str.strip("_") # Elimina guiones bajos al principio y al final
                            .str.lower() # Pone todo en minúsculas
                            .str.title() # Primera letra en mayúsculas
                )
    return df

# Función para eliminar columnas
def eliminar_columnas(df, cols):
    """Esta función elimina las columnas que se le pasen como argumento.

    Args:
        df (pd.Dataframe): dataframe a eliminar columnas.
        cols (list): Lista con los nombres de las columnas a eliminar.

    Returns: dataframe sin las columnas a eliminar.
    """    
    return df.drop(columns=cols, axis=1, inplace=True)

# Función para concatenar nombres
def concatenar_nombres(df,col1,col2):
    """Esta función concatena los valores de las columnas que se le pasen como argumento.

    Args:
        df (pd.Dataframe): dataframe a concatenar nombres.
        cols (list): lista con los nombres de las columnas a concatenar.

    Returns: dataframe con los nombres concatenados.
    """    
    df['Full_Name'] = df[col1].str.strip() + ' ' + df[col2].str.strip() # Aplicamos la función strip para eliminar posibles espacios al principio y al final
    eliminar_columnas(df, [col1, col2]) # Eliminamos las columnas que ya no necesitamos
    return df

# Función para convertir a datetime una lista de columnas
def convertir_datetime(df,cols):
    """Esta función convierte a datetime una lista de columnas.

    Args:
        df (pd.Dataframe): dataframe a modificar.
        cols (list): lista de columnas a convertir.

    Returns: dataframe modificado.
    """    
    for col in cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

# Función para dejar sólo la fecha en una columna de tipo datetime
def solo_fecha(df,cols):
    """Esta función elimina la hora de una lista de columnas de tipo datetime.

    Args:
        df (pd.Dataframe): dataframe a modificar.
        cols (str): lista de columnas modificar.

    Returns: dataframe modificado.
    """    
    for col in cols:
        df[col] = pd.to_datetime(df[col]).dt.date
    return df

# Función para convertir a datetime una lista de columnas y dejar sólo la fecha

def fecha(df,cols):
    """Esta función deja sólo la fecha de un campo fecha-hora y convierte a datetime una lista de columnas.

    Args:
        df (pd.Dataframe): dataframe a modificar.
        cols (list): lista de columnas a convertir.

    Returns: dataframe modificado.
    """    
    solo_fecha(df,cols)
    convertir_datetime(df,cols)

# Función para reemplazar los valores de una columna por un diccionario
def reemplazar_valores_columna(df,col,diccionario):
    """Esta función reemplaza los valores de una columna por un diccionario.

    Args:
        df (pd.Dataframe): dataframe a modificar.
        col (str): nombre de la columna a modificar.
        diccionario (dict): diccionario con los valores a reemplazar.

    Returns: dataframe modificado.
    """    
    df[col] = df[col].map(diccionario)


# Funcion para calcula r la edad a partir de la fecha de nacimiento
def calcular_edad(df,col_input, col_output):
    """Esta función calcula la diferencia en años hasta hoy a partir de una fecha.

    Args:
        df (pd.Dataframe): dataframe a modificar.
        col (str): nombre de la columna a modificar.

    Returns: dataframe modificado.
    """    
    df[col_output] = datetime.now().year - pd.to_datetime(df[col_input]).dt.year
    eliminar_columnas(df, [col_input]) # Eliminamos la columna que ya no necesitamos
    return df

# Función para convertir valores de tipo float a integer
def convertir_float_int(df,columns):
    """Esta función convierte valores de tipo float a integer.

    Args:
        df (pd:Datafreme): dataframe a modificar.
        columns (list): lista de columnas a modificar.

    Returns: dataframe convertido
    """    
    for col in columns:
        df[col] = df[col].astype('Int64')


