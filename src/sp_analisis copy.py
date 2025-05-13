'''Este archivo contiene las funciones que se utilizan en los archivos principales del proyecto'''

# Importamos las librerías necesarias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

# Función para homogeneización de datos categóricos
def homogeneizacion_categoricos(df):
    """Esta función homogeneiza los datos categóricos, poniéndolos en minúsculas.

    Args:
        df (pd.Dataframe): dataframe a homogeneizar.

    Returns: dataframe modificado.
    """    
    for col in df.select_dtypes(include='O').columns:
        df[col] = df[col].str.lower()


# Función para cambiar las columnas de tipo de dato object a float
def obj_float(df,cols):
    """Esta función cambia las columnas de tipo de datos object a float.

    Args:
        df (pd.Dataframe): dataframe a modificar.
        cols (list): lista de columnas a modificar.

    Returns: dataframe modificado.
    """
    for col in cols:
        df[col] = df[col].str.replace(',', '.')
        df[col] = df[col].apply(lambda x: float(x))

# Función para cambiar las columnas de tipo de dato float a object
def float_object(df,cols):
    """Esta función cambia las columnas de tipo de datos float a object.

    Args:
        df (pd.Dataframe): dataframe a modificar.
        cols (list): lista de columnas a modificar.

    Returns: dataframe modificado.
    """    
    # Primero: creamos un diccionario de mapeo para cambiar los valores de 'yes' y 'no' a 1 y 0 respectivamente
    dicc_mapeo = {1:'yes', 0:'no'}
    float_obj = ['Default', 'Housing', 'Loan']

    # Segundo: aplicamos el mapeo a las columnas
    for col in float_obj:    
        df[col] = df[col].map(dicc_mapeo)


# Función para homogeneizar los valores de la columna 'Education'
def homogeneizacion_valores_columna(df,col):
    """Esta función reemplaza:
        - Reemplaza '.' por '_'

    Args:
        df (pd.Dataframe): dataframe a modificar.
        cols (str): nombre de la columna a modificar.

    Returns: dataframe modificado.
    """    
    df[col] = df[col].str.replace('M','Male')
    df[col] = df[col].str.replace('F','Female')

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

# Función que obtiene la matriz de correlación de las variables numéricas
def matriz_corr(df):
    """Obtiene la matriz de correlación para las variables numéricas.

    Args:
        df (pd.Dataframe): Dataframe del que queremos la matriz de correlación.
    
    Returns: matriz de correlación.
    """    
    df_copia=df.copy()
    df_copia['Y'] = df_copia['Y'].map({'no': 0, 'yes': 1})
    plt.figure(figsize=(10,5))
    mask = np.triu(np.ones_like(df_copia.corr(numeric_only=True), dtype=bool))
    sns.heatmap(data=df_copia.corr(numeric_only=True), annot=True, vmin=-1 , vmax=1, cmap="coolwarm", linecolor="black", fmt=".2f", mask=mask)
    plt.title("Matriz de correlación (incluyendo y)")
    plt.show()  

# 4. GESTIÓN DE NULOS --------------------------------------------------------------

# Función para obtener el % de nulos y las frecuencias
def frec_cat_y_nulos(df):
    """Esta función obtiene para cada variable categórica:
        - El porcentaje de nulos
        - Los valores únicos
        - Las frecuencias de los valores 

    Args:
        df (pd.Dataframe): dataframe del que queremos obtener las frecuencias.
    
    Returns: dataframe con porcentaje de nulos, valores únicos y frecuencias de los valores.
    """   
    print('La distribución de frecuencias de las variables categóricas es:\n')
    df_cat = df.select_dtypes(include ='O')
    for col in df_cat.columns:
        print(f'En la columna {col.upper()} los valores nulos son:')
        print(f'{round(df_cat[col].isnull().sum()/df.shape[0]*100,2)}%\n')
        frec = df_cat[col].value_counts()
        porc = round(frec/df_cat.shape[0]*100,2)
        df_aux = pd.DataFrame({'Frecuencia' : frec,
                               'Porcentaje' : porc})
        print(f'Para la columna {col.upper()}, los valores únicos son:')
        print(df[col].unique())
        display(df_aux)
        print ('-'*50)  

# Función para ver % de nulos y las frecuencias de las variables numéricas
def frec_num_y_nulos(df):
    """Esta función obtiene para cada variable numérica:
        - El porcentaje de nulos
        - Las frecuencias de los valores 

    Args:
        df (pd.Dataframe): dataframe del que queremos obtener las frecuencias.
    
    Returns: dataframe con porcentaje de nulos y frecuencias de los valores.
    """  
    df_num = df.select_dtypes(include = np.number)
    col_nulos_num = df[df.columns[df.isnull().any()]].select_dtypes(include = np.number).columns
    if len(col_nulos_num) == 0:
        print("No hay columnas categóricas con valores nulos")
        print('-'*50)
    else:
        for col in df_num.columns:
            print(f'En la columna {col.upper()} los valores nulos son:')
            print(f'{round(df[col].isnull().sum()/df.shape[0]*100,2)}%\n')
            frec = df_num[col].value_counts()
            porc = round(frec/df_num.shape[0]*100,2)
            df_aux = pd.DataFrame({'Frecuencia' : frec,
                                    'Porcentaje' : porc})
            display(df_aux)
            print('-'*50)

# Función para calcular el % de nulos
def analisis_nulos_frecuencias(df):
    """Esta función realiza las siguientes tareas:
         - Obtiene el % de nulos de todas las columnas
         - Obtiene el % de nulos y la frecuencia de los valores para las columnas categóricas
         - Obtiene el % de nulos y la frecuencia de los valores para las columnas numéricas

    Args:
        df (pd.Dataframe): dataframe del que queremos obtener la información.

    Returns: valores nulos.
    """    
    # Primero: obtenemos el % de nulos de todas las columnas
    nulos_col(df)
    
    # Segundo: obtenemos las columnas categóricas, el % de nulos, los valores únicos y la frecuencia de los valores para cada una de ellas
    print("🔠 COLUMNAS CATEGÓRICAS")
    col_nulos_cat = df[df.columns[df.isnull().any()]].select_dtypes(include='O').columns
    if len(col_nulos_cat) == 0:
        print("No hay columnas categóricas con valores nulos")
        print('-'*50)
    else:
        frec_cat_y_nulos(df)

    # Tercero: obtenemos las columnas numéricas, el % de nulos y la frecuencia de los valores para cada una de ellas
    print("🔢 COLUMNAS NUMÉRICAS")
    frec_num_y_nulos(df) 

# Función para rellenar los nulos de las categóricas como 'unknown'
def rellenar_unknown_cat(df,cols):
    """Esta función rellena los valores nulos por 'unkwnown'.

    Args:
        df (pd.Dataframe): dataframe a modificar.
        cols (list): columnas en las que queremos realizar el cambio.

    Returns: dataframe con valores nulos rellenados por 'unknown'.
    """    
    for col in cols:
        df[col] = df[col].fillna('unknown')
        # df[col].fillna('unknown', inplace = True) # Este método ya no será válido en el futuro

# Función para rellenar los nulos de las categóricas por la moda
def rellenar_moda_cat(df,cols):
    """Esta función rellena los valores nulos por la moda de la columna correspondiente.

    Args:
        df (pd.Dataframe): dataframe a modificar.
        cols (list): lista de columnas a modificar.

    Returns: dataframe con valores nulos rellenados por la moda.
    """    
    for col in cols:
        if col == 'Marital':
            df[col] = df[col].fillna('married')
        elif col == 'Loan':
            df[col] = df[col].fillna('no')
        else:
            print("Columna no incluida en lista 'col_cat_moda'")
        
# Función para rellenar nulos de las categóricas con 'unknown' y por la moda
def rellenar_nulos_cat(df, cols):
    """Esta función rellena los nulos de las columnas categóricas y los reemplaza por 'unknown' o por la moda,
       en función de lo que se indique para cada columna.  

    Args:
        df (pd.Dataframe): dataframe a modificar.
        cols (dict): diccionario de columnas a modificar.
    
    Returns: dataframe con valores nulos rellenados por 'unknown' o la moda.
    """    
    for key,value in cols.items():
        if key == "col_cat_unknown":
            rellenar_unknown_cat(df, value)
        elif key == "col_cat_moda":
            rellenar_moda_cat(df,value)
        else:
            print('Columna no encontrada')

# Función para representar boxplots para detectar outliers
def outliers_num(df):
    """Esta función comprueba la existencia o no de valores nulos en columnas numéricas y, en caso afirmativo,
       realiza boxplot de cada columna.

    Args:
        df (pd.Dataframe): dataframe a analizar
    
    Returns: boxplot de cada columna numérica con valores nulos.
    """    
    col_nulos_num = df[df.columns[df.isnull().any()]].select_dtypes(include = np.number).columns
    if len(col_nulos_num) == 0:
        print("No hay columnas numéricas con valores nulos")
        print('-'*50)
    else:
        fig, axes = plt.subplots(nrows = len(col_nulos_num), ncols = 1, figsize = (10, 10))
        for i in range(len(col_nulos_num)):
            sns.boxplot(x = col_nulos_num[i], data=df, ax = axes[i], legend = False, color = '#008289')

# Función para rellenar nulos de las numéricas con media o mediana
def rellenar_nulos_num_media_mediana(df,dict_cols_num):
    """Esta función rellena los nulos de las varibles numéricas dependiendo de las columnas que le pasemos mediante un diccionario:
        - Si pasamos un item cuya key sea 'cols_to mediana', rellena los nulos con la mediana
        - Si pasamos un item cuya key sea 'cols_to_media_mediana', calculará cuál de ellas tiene menos error y rellenará los nulos con la que tenga menos error

    Args:
        df (pd.Dataframe): dataframe a modificar.
        dict_cols_num (dict): diccionario que contiene las columnas a modificar.

    Returns: dataframe con nulos rellenados por media o mediana.    
    """    
    for key,value in dict_cols_num.items():
        for col in value:
            media = df[col].mean()
            mediana = df[col].median()    
            if key == 'cols_to_mediana':
                df[col] = df[col].fillna(mediana)
                print(f'Se han sustituido los nulos de la columna {col} por su mediana {mediana}.')
                print('-'*50)
            elif key == 'cols_to_media_mediana':
                df_aux = df[col].reset_index()
                df_aux['media'] = df[col].fillna(media)
                df_aux['mediana'] = df[col].fillna(mediana)
                error_media = abs(df_aux['media'].std())
                error_mediana = abs(df_aux['mediana'].std())
                if error_media <= error_mediana:
                    df[col] = df[col].fillna(media)
                    print(f'Para la columna {col}, el error es menor con la media.')
                    print(f'Los valores nulos se rellenaron con la media: {media}')
                    print('-'*50)
                else:
                    df[col] = df[col].fillna(mediana)
                    print(f'Para la columna {col}, el error es menor con la mediana.')
                    print(f'Los valores nulos se rellenaron con la mediana: {mediana}')
            else:
                print('No hay columnas con valores nulos')

# 5. VISUALIZACIONES ---------------------------------------------------------------

# Función para representar las variables categóricas
def graficos_cat(df):
    """Esta función representa gráficos de barras de las variables categóricas de un Dataframe.

    Args:
        df (pd.Dataframe): dataframe del que queremos obtener los gráficos de barras.
    
    Returns: gráficos de barras.
    """    
    cols_cat = [col for col in df.select_dtypes(include=['O']).columns if col != 'Id']
    num_rows = len(cols_cat)

    fig, axes = plt.subplots(num_rows,1, figsize=(15,50))

    axes = axes.flatten()

    for i, col in enumerate(cols_cat):
        sns.countplot(data=df, x=col, palette='mako', hue=col, ax=axes[i])
        axes[i].set_title(f'Barplot de {col}')
        axes[i].set_ylabel(f'Frecuencia')
        axes[i].set_xlabel('')

# Función para representar las variables numéricas
def graficos_num(df):
    """Esta función representa los histogramas y boxplosts de las variables numéricas de un Dataframe.

    Args:
        df (pd.Dataframe): dataframe del que queremos obtener los histogramas y boxplots.
    
    Returns: histogramas y boxplots.
    """ 
    cols_num = [col for col in df.select_dtypes(include=[np.number]).columns if col != 'Year' and col != 'Month' and col!= 'Day']
    num_rows = len(cols_num)

    fig, axes = plt.subplots(num_rows,2, figsize=(14,50))

    for i,col in enumerate(cols_num):
        sns.histplot(data=df, x=col, ax=axes[i,0])
        axes[i,0].set_title(f'Histplot de {col}')
        axes[i,0].set_xlabel('')
        sns.boxplot(data=df, x=col, ax=axes[i,1])
        axes[i,1].set_title(f'Boxplot de {col}')
        axes[i,1].set_xlabel('')

# Función que representa las graficas de todas las variables
def visualizaciones(df):
    """Esta función agrupa a las funciones: 
        - graficos_cat
        - frecuencia_valores
        - graficos_num

    Args:
        df (pd.Dataframe): dataframe del que queremos obtener las visualizaciones.
    
    Returns: visualizaciones.
    """   
    graficos_cat(df)
    frec_cat(df)
    graficos_num(df)



