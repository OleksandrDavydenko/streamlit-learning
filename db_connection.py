import os
import pyodbc
import pandas as pd
from datetime import datetime

def _get_secret(key, default=None):
    """Try to read secret from Streamlit secrets (if available) or environment."""
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val is not None:
            return val
    except Exception:
        pass

    # fallback to environment variables
    return os.environ.get(key, default)


def get_connection():
    """Підключення до SQL Server. Параметри читаються зі секретів/перемінних оточення."""
    SERVER = _get_secret("SERVER")
    DATABASE = _get_secret("DATABASE")
    USERNAME = _get_secret("USERNAME") or _get_secret("UID")
    PASSWORD = _get_secret("PASSWORD") or _get_secret("PWD")

    if not all([SERVER, DATABASE, USERNAME, PASSWORD]):
        raise RuntimeError("Missing database connection settings. Set SERVER, DATABASE, USERNAME and PASSWORD in secrets or environment variables.")

    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={SERVER};'
            f'DATABASE={DATABASE};'
            f'UID={USERNAME};'
            f'PWD={PASSWORD}'
        )
        return conn
    except Exception as e:
        raise


def get_expenses_data():
    """Отримати дані про витрати з БД

    Повертає pandas.DataFrame
    """
    conn = None
    try:
        conn = get_connection()
    except Exception as e:
        print(f"Помилка підключення: {e}")
        return pd.DataFrame()

    query = """
    SELECT
        CAST(YEAR(d._Date_Time) - 2000 AS VARCHAR(4)) + '-' + FORMAT(d._Date_Time, 'MM') + '-' + FORMAT(d._Date_Time, 'dd') as 'Period',
        CASE 
            WHEN department._Description IS NULL OR department._Description = 'Адміністрація' THEN 'Інше'
            ELSE department._Description
        END as 'Department',
        COALESCE(type_of_expense._Description, 'Витрати не профітцентрів') as 'Type_of_expense',
        COALESCE(parent_expense._Description, 'Витрати не профітцентрів') as 'Parent_Description',
        t._Fld15249 as 'Sum',
        CASE
            When type_of_expense._Fld15216RRef = 0xB3BDB34D1CF80C2546F6A8E3D8F0F9BF
                then 'Прямий'
            When type_of_expense._Fld15216RRef = 0x9368DC35A1C76CC04338B75DBB622F6C
                then 'Не розподіляти'
            When type_of_expense._Fld15216RRef = 0xB6E7A38332318608440F3C2401C15229
                then 'На профітцентри'
            Else 'Невизначено'
        END as 'DistributionBase'
        
    FROM 
        [expeditor].[dbo].[_Document15134_VT15245] as t
    LEFT JOIN 
        [dbo].[_Document15134] as d ON d._IDRRef = t._Document15134_IDRRef
    LEFT JOIN 
        [dbo].[_Reference13165] as department ON department._IDRRef = t._Fld15250RRef
    LEFT JOIN 
        [dbo].[_Reference4924] as type_of_expense ON type_of_expense._IDRRef = t._Fld15248RRef
    LEFT JOIN 
        [dbo].[_Reference4924] as parent_expense ON parent_expense._IDRRef = type_of_expense._ParentIDRRef

    WHERE
         CAST(YEAR(d._Date_Time) - 2000 AS VARCHAR(4)) + '-' + FORMAT(d._Date_Time, 'MM') + '-' + FORMAT(d._Date_Time, 'dd') >= '2024-01-01'
         AND
         d._Marked = 0x00
         AND
         d._Posted = 0x01
    """
    try:
        df = pd.read_sql(query, conn)
        df['Sum'] = pd.to_numeric(df['Sum'], errors='coerce')
        df['Period'] = pd.to_datetime(df['Period'])
        return df
    except Exception as e:
        print(f"Помилка запиту: {e}")
        return pd.DataFrame()
    finally:
        try:
            if conn is not None:
                conn.close()
        except Exception:
            pass
