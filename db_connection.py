# -*- coding: utf-8 -*-
import os
import requests
import pandas as pd


def _get_secret(key: str, default: str = "") -> str:
    """Читає секрет зі Streamlit secrets або змінних оточення."""
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val is not None:
            return str(val)
    except Exception:
        pass
    return os.environ.get(key, default)


def _get_token() -> str:
    """Отримує Bearer-токен через ROPC (Resource Owner Password Credentials)."""
    client_id = _get_secret("PBI_CLIENT_ID")
    username  = _get_secret("PBI_USERNAME")
    password  = _get_secret("PBI_PASSWORD")
    scope     = "https://analysis.windows.net/powerbi/api"
    token_url = "https://login.microsoftonline.com/common/oauth2/token"

    if not all([client_id, username, password]):
        raise RuntimeError("Не задані PBI_CLIENT_ID, PBI_USERNAME або PBI_PASSWORD у секретах.")

    body = {
        "grant_type": "password",
        "resource": scope,
        "client_id": client_id,
        "username": username,
        "password": password,
    }
    r = requests.post(token_url, data=body,
                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                      timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


def _exec_dax(token: str, dataset_id: str, dax: str) -> dict:
    """Виконує DAX-запит до Power BI REST API."""
    url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/executeQueries"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "queries": [{"query": dax}],
        "serializerSettings": {"includeNulls": True},
    }
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def _to_dataframe(result_json: dict) -> pd.DataFrame:
    """Перетворює відповідь PBI API на DataFrame."""
    results = result_json.get("results", [])
    tables  = results[0].get("tables", []) if results else []
    if not tables:
        return pd.DataFrame()
    table = tables[0]
    cols  = [c.get("name") for c in table.get("columns", [])] if table.get("columns") else []
    rows  = table.get("rows", []) or []
    out = []
    for row in rows:
        if isinstance(row, dict):
            out.append(row)
        else:
            out.append({cols[i]: row[i] for i in range(len(cols))})

    def clean(k: str) -> str:
        return k.split("[", 1)[-1].rstrip("]") if "[" in k else k

    return pd.DataFrame([{clean(k): v for k, v in rec.items()} for rec in out])


def get_expenses_data() -> pd.DataFrame:
    """Отримати таблицю Operating_Expenses_SQL з Power BI і повернути DataFrame."""
    dataset_id = _get_secret("PBI_DATASET_ID")
    if not dataset_id:
        raise RuntimeError("Не задано PBI_DATASET_ID у секретах.")

    token = _get_token()

    dax = "EVALUATE 'Operating_Expenses_SQL'"
    result = _exec_dax(token, dataset_id, dax)
    df = _to_dataframe(result)

    if df.empty:
        return df

    # Типізація
    if "Sum" in df.columns:
        df["Sum"] = pd.to_numeric(df["Sum"], errors="coerce")
    if "Period" in df.columns:
        df["Period"] = pd.to_datetime(df["Period"], errors="coerce")

    return df
