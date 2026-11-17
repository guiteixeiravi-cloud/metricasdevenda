from datetime import datetime, timedelta, timezone
import pandas as pd
import requests
import streamlit as st

FIREBASE_URL = "https://loguii-default-rtdb.firebaseio.com/sistema_vendas_2026"
FUSO_BR = timezone(timedelta(hours=-3))

USUARIOS = {
    "guiadm": {
        "senha": "programacaoteste",
        "nome": "Guilherme",
        "label": "Usuário 1 — Guilherme (guiadm)",
        "perfil": "admin",
    },
    "samarete": {
        "senha": "samaretevidalouca",
        "nome": "Samara",
        "label": "Samara (samarete)",
        "perfil": "user",
    },
}

HISTORICO_2026_USUARIO_1 = {
    "init_2026_01": {"data": "2026-01-31", "hora": "18:00", "usuario": "guiadm", "valor": 117343.52, "observacao": "Fechamento Janeiro/2026"},
    "init_2026_02": {"data": "2026-02-28", "hora": "18:00", "usuario": "guiadm", "valor": 102232.69, "observacao": "Fechamento Fevereiro/2026"},
    "init_2026_03": {"data": "2026-03-31", "hora": "18:00", "usuario": "guiadm", "valor": 121330.00, "observacao": "Fechamento Março/2026"},
    "init_2026_04": {"data": "2026-04-30", "hora": "18:00", "usuario": "guiadm", "valor": 137153.08, "observacao": "Fechamento Abril/2026"},
    "init_2026_05": {"data": "2026-05-31", "hora": "18:00", "usuario": "guiadm", "valor": 107225.29, "observacao": "Fechamento Maio/2026"},
    "init_2026_06": {"data": "2026-06-30", "hora": "18:00", "usuario": "guiadm", "valor": 136796.42, "observacao": "Fechamento Junho/2026"},
    "init_2026_07": {"data": "2026-07-31", "hora": "18:00", "usuario": "guiadm", "valor": 148812.13, "observacao": "Fechamento Julho/2026"},
    "init_2026_08": {"data": "2026-08-31", "hora": "18:00", "usuario": "guiadm", "valor": 152361.81, "observacao": "Fechamento Agosto/2026"},
    "init_2026_09": {"data": "2026-09-30", "hora": "18:00", "usuario": "guiadm", "valor": 201982.79, "observacao": "Fechamento Setembro/2026"},
    "init_2026_10": {"data": "2026-10-31", "hora": "18:00", "usuario": "guiadm", "valor": 178483.27, "observacao": "Fechamento Outubro/2026"},
    "init_2026_11": {"data": "2026-11-17", "hora": "12:00", "usuario": "guiadm", "valor": 81636.40, "observacao": "Acumulado Parcial Novembro/2026"},
}

METAS_INICIAIS_2026 = {
    "2026-01_guiadm": {"ano_mes": "2026-01", "usuario": "guiadm", "meta": 110000.00},
    "2026-02_guiadm": {"ano_mes": "2026-02", "usuario": "guiadm", "meta": 100000.00},
    "2026-03_guiadm": {"ano_mes": "2026-03", "usuario": "guiadm", "meta": 105000.00},
    "2026-04_guiadm": {"ano_mes": "2026-04", "usuario": "guiadm", "meta": 105000.00},
    "2026-05_guiadm": {"ano_mes": "2026-05", "usuario": "guiadm", "meta": 120000.00},
    "2026-06_guiadm": {"ano_mes": "2026-06", "usuario": "guiadm", "meta": 125000.00},
    "2026-07_guiadm": {"ano_mes": "2026-07", "usuario": "guiadm", "meta": 130000.00},
    "2026-08_guiadm": {"ano_mes": "2026-08", "usuario": "guiadm", "meta": 140000.00},
    "2026-09_guiadm": {"ano_mes": "2026-09", "usuario": "guiadm", "meta": 150000.00},
    "2026-10_guiadm": {"ano_mes": "2026-10", "usuario": "guiadm", "meta": 150000.00},
    "2026-11_guiadm": {"ano_mes": "2026-11", "usuario": "guiadm", "meta": 150000.00},
    "2026-12_guiadm": {"ano_mes": "2026-12", "usuario": "guiadm", "meta": 150000.00},
}

NOMES_MESES = {
    "01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr",
    "05": "Mai", "06": "Jun", "07": "Jul", "08": "Ago",
    "09": "Set", "10": "Out", "11": "Nov", "12": "Dez",
}


def agora_brasil() -> datetime:
    return datetime.now(FUSO_BR)


def formatar_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_comissao(vendido: float, meta: float) -> tuple[float, float, float]:
    comissao_base = vendido * 0.0015
    excedente = max(0.0, vendido - meta)
    bonus_meta = excedente * 0.005
    return comissao_base, bonus_meta, comissao_base + bonus_meta


def carregar_dados_firebase() -> tuple[pd.DataFrame, pd.DataFrame, bool]:
    try:
        resp_v = requests.get(f"{FIREBASE_URL}/vendas.json", timeout=10)
        resp_v.raise_for_status()
        dados_v = resp_v.json()

        if not dados_v:
            requests.put(
                f"{FIREBASE_URL}/vendas.json",
                json=HISTORICO_2026_USUARIO_1,
                timeout=10,
            ).raise_for_status()
            dados_v = HISTORICO_2026_USUARIO_1

        resp_m = requests.get(f"{FIREBASE_URL}/metas.json", timeout=10)
        resp_m.raise_for_status()
        dados_m = resp_m.json()

        if not dados_m:
            requests.put(
                f"{FIREBASE_URL}/metas.json",
                json=METAS_INICIAIS_2026,
                timeout=10,
            ).raise_for_status()
            dados_m = METAS_INICIAIS_2026

        lista_v = []
        for reg_id, item in dados_v.items():
            if isinstance(item, dict):
                lista_v.append(
                    {
                        "id": reg_id,
                        "data": item.get("data"),
                        "hora": item.get("hora", "--:--"),
                        "usuario": item.get("usuario", "guiadm"),
                        "valor": float(item.get("valor", 0.0)),
                        "observacao": item.get("observacao", "Venda diária"),
                    }
                )

        lista_m = []
        for reg_id, item in dados_m.items():
            if isinstance(item, dict):
                lista_m.append(
                    {
                        "id": reg_id,
                        "ano_mes": item.get("ano_mes"),
                        "usuario": item.get("usuario", "guiadm"),
                        "meta": float(item.get("meta", 0.0)),
                    }
                )

        df_v = pd.DataFrame(lista_v)
        df_m = pd.DataFrame(lista_m)

        df_v["data"] = pd.to_datetime(df_v["data"])
        df_v = df_v[df_v["data"].dt.year >= 2026].copy()
        df_v["ano_mes"] = df_v["data"].dt.strftime("%Y-%m")
        df_v["data_str"] = df_v["data"].dt.strftime("%Y-%m-%d")

        return df_v, df_m, True

    except Exception as erro:
        st.error(f"Erro ao conectar com o Firebase: {erro}")
        df_v = pd.DataFrame([{"id": k, **v} for k, v in HISTORICO_2026_USUARIO_1.items()])
        df_v["data"] = pd.to_datetime(df_v["data"])
        df_v["ano_mes"] = df_v["data"].dt.strftime("%Y-%m")
        df_v["data_str"] = df_v["data"].dt.strftime("%Y-%m-%d")
        df_m = pd.DataFrame([{"id": k, **v} for k, v in METAS_INICIAIS_2026.items()])
        return df_v, df_m, False


def registrar_venda_rapida(usuario: str, valor: float) -> bool:
    agora = agora_brasil()
    payload = {
        "data": agora.strftime("%Y-%m-%d"),
        "hora": agora.strftime("%H:%M"),
        "usuario": usuario,
        "valor": float(valor),
        "observacao": f"Venda rápida ({agora.strftime('%H:%M')})",
    }
    resp = requests.post(f"{FIREBASE_URL}/vendas.json", json=payload, timeout=10)
    return resp.status_code == 200


def excluir_venda_firebase(reg_id: str) -> bool:
    resp = requests.delete(f"{FIREBASE_URL}/vendas/{reg_id}.json", timeout=10)
    return resp.status_code == 200


def salvar_meta_firebase(ano_mes: str, usuario: str, meta: float) -> bool:
    chave = f"{ano_mes}_{usuario}"
    payload = {
        "ano_mes": ano_mes,
        "usuario": usuario,
        "meta": float(meta),
    }
    resp = requests.put(f"{FIREBASE_URL}/metas/{chave}.json", json=payload, timeout=10)
    return resp.status_code == 200
