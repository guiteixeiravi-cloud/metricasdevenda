import io
import os
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

FIREBASE_URL = "https://loguii-default-rtdb.firebaseio.com/sistema_vendas_2026"


def obter_caminho_logo() -> str | None:
    for nome_arquivo in ["logo.png", "Analista de Dados em Ação.png"]:
        if os.path.exists(nome_arquivo):
            return nome_arquivo
    return None


CAMINHO_LOGO = obter_caminho_logo()

st.set_page_config(
    page_title="Gestão de Vendas & Comissões 2026",
    page_icon=CAMINHO_LOGO if CAMINHO_LOGO else "📈",
    layout="wide",
)

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
    "init_2026_01": {"data": "2026-01-31", "usuario": "guiadm", "valor": 117343.52, "observacao": "Fechamento Janeiro/2026"},
    "init_2026_02": {"data": "2026-02-28", "usuario": "guiadm", "valor": 102232.69, "observacao": "Fechamento Fevereiro/2026"},
    "init_2026_03": {"data": "2026-03-31", "usuario": "guiadm", "valor": 121330.00, "observacao": "Fechamento Março/2026"},
    "init_2026_04": {"data": "2026-04-30", "usuario": "guiadm", "valor": 137153.08, "observacao": "Fechamento Abril/2026"},
    "init_2026_05": {"data": "2026-05-31", "usuario": "guiadm", "valor": 107225.29, "observacao": "Fechamento Maio/2026"},
    "init_2026_06": {"data": "2026-06-30", "usuario": "guiadm", "valor": 136796.42, "observacao": "Fechamento Junho/2026"},
    "init_2026_07": {"data": "2026-07-31", "usuario": "guiadm", "valor": 148812.13, "observacao": "Fechamento Julho/2026"},
    "init_2026_08": {"data": "2026-08-31", "usuario": "guiadm", "valor": 152361.81, "observacao": "Fechamento Agosto/2026"},
    "init_2026_09": {"data": "2026-09-30", "usuario": "guiadm", "valor": 201982.79, "observacao": "Fechamento Setembro/2026"},
    "init_2026_10": {"data": "2026-10-31", "usuario": "guiadm", "valor": 178483.27, "observacao": "Fechamento Outubro/2026"},
    "init_2026_11": {"data": "2026-11-17", "usuario": "guiadm", "valor": 81636.40, "observacao": "Acumulado Parcial Novembro/2026"},
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
    "01": "Jan",
    "02": "Fev",
    "03": "Mar",
    "04": "Abr",
    "05": "Mai",
    "06": "Jun",
    "07": "Jul",
    "08": "Ago",
    "09": "Set",
    "10": "Out",
    "11": "Nov",
    "12": "Dez",
}


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
                        "usuario": item.get("usuario", "guiadm"),
                        "valor": float(item.get("valor", 0.0)),
                        "observacao": item.get("observacao", ""),
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

        return df_v, df_m, True

    except Exception as erro:
        st.error(f"Erro ao conectar com o Firebase: {erro}")
        df_v = pd.DataFrame(
            [{"id": k, **v} for k, v in HISTORICO_2026_USUARIO_1.items()]
        )
        df_v["data"] = pd.to_datetime(df_v["data"])
        df_v["ano_mes"] = df_v["data"].dt.strftime("%Y-%m")
        df_m = pd.DataFrame(
            [{"id": k, **v} for k, v in METAS_INICIAIS_2026.items()]
        )
        return df_v, df_m, False


def adicionar_venda_firebase(data_venda: date, usuario: str, valor: float, observacao: str) -> bool:
    payload = {
        "data": data_venda.strftime("%Y-%m-%d"),
        "usuario": usuario,
        "valor": float(valor),
        "observacao": observacao,
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


def tela_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if CAMINHO_LOGO:
            c_img1, c_img2, c_img3 = st.columns([1, 1.4, 1])
            with c_img2:
                st.image(CAMINHO_LOGO, use_container_width=True)

        st.markdown("## 🔐 Acesso ao Sistema de Vendas 2026")
        st.caption("Entre com suas credenciais para visualizar metas, vendas e comissões.")

        with st.form("form_login"):
            login = st.text_input("Usuário").strip().lower()
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar", use_container_width=True)

            if entrar:
                if login in USUARIOS and USUARIOS[login]["senha"] == senha:
                    st.session_state["usuario_logado"] = login
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")


def app_principal():
    login = st.session_state["usuario_logado"]
    info_user = USUARIOS[login]
    eh_admin = info_user["perfil"] == "admin"

    df_v, df_m, conectado_firebase = carregar_dados_firebase()

    # Barra lateral
    with st.sidebar:
        if CAMINHO_LOGO:
            st.image(CAMINHO_LOGO, use_container_width=True)
            st.divider()

        st.markdown(f"### 👤 {info_user['label']}")
        st.caption(f"Perfil: **{'Administrador (Usuário 1)' if eh_admin else 'Vendedora'}**")

        if conectado_firebase:
            st.success("🟢 Nuvem Firebase conectada")
        else:
            st.warning("🟡 Modo offline temporário")

        if st.button("🔄 Sincronizar Dados", use_container_width=True):
            st.rerun()

        st.divider()

        if eh_admin:
            filtro_usuario = st.selectbox(
                "Visualizar dados de:",
                options=["guiadm", "samarete", "TODOS"],
                format_func=lambda x: (
                    "Consolidado (Todos)"
                    if x == "TODOS"
                    else USUARIOS[x]["label"]
                ),
            )
        else:
            filtro_usuario = login

        meses_disponiveis = sorted(
            list(set(df_m["ano_mes"].tolist() + df_v["ano_mes"].tolist())),
            reverse=True,
        )
        mes_atual_str = date.today().strftime("%Y-%m")
        idx_padrao = (
            meses_disponiveis.index(mes_atual_str)
            if mes_atual_str in meses_disponiveis
            else 0
        )

        mes_selecionado = st.selectbox(
            "Mês de Referência (2026+)",
            options=meses_disponiveis,
            index=idx_padrao,
            format_func=lambda ym: f"{NOMES_MESES.get(ym.split('-')[1], ym)}/{ym.split('-')[0]}",
        )

        st.divider()
        if st.button("Sair", use_container_width=True):
            del st.session_state["usuario_logado"]
            st.rerun()

    # Cabeçalho principal com logo e boas-vindas
    if CAMINHO_LOGO:
        col_logo, col_titulo = st.columns([0.13, 0.87], vertical_alignment="center")
        with col_logo:
            st.image(CAMINHO_LOGO, use_container_width=True)
        with col_titulo:
            st.markdown(f"## 👋 Bem vindo, {info_user['nome']}")
            st.markdown("### 📊 Painel de Vendas, Metas e Comissões (2026+)")
    else:
        st.markdown(f"## 👋 Bem vindo, {info_user['nome']}")
        st.title("📊 Painel de Vendas, Metas e Comissões (2026+)")

    # Filtragem por usuário
    if filtro_usuario == "TODOS":
        df_v_filtrado = df_v.copy()
        df_m_filtrado = df_m.copy()
    else:
        df_v_filtrado = df_v[df_v["usuario"] == filtro_usuario].copy()
        df_m_filtrado = df_m[df_m["usuario"] == filtro_usuario].copy()

    # Cálculos do mês selecionado
    vendido_mes = df_v_filtrado[df_v_filtrado["ano_mes"] == mes_selecionado]["valor"].sum()
    meta_mes = df_m_filtrado[df_m_filtrado["ano_mes"] == mes_selecionado]["meta"].sum()
    com_base, com_bonus, com_total = calcular_comissao(vendido_mes, meta_mes)
    falta_meta = max(0.0, meta_mes - vendido_mes)
    excedente_meta = max(0.0, vendido_mes - meta_mes)
    pct_meta = (vendido_mes / meta_mes * 100) if meta_mes > 0 else 0.0

    # Cards principais
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento no Mês", formatar_brl(vendido_mes), f"{pct_meta:.1f}% da meta")
    c2.metric("Meta do Mês", formatar_brl(meta_mes))
    if excedente_meta > 0:
        c3.metric("Superação da Meta", formatar_brl(excedente_meta), "Meta batida! 🚀")
    else:
        c3.metric("Falta para Meta", formatar_brl(falta_meta))
    c4.metric(
        "Comissão Total Estimada",
        formatar_brl(com_total),
        f"Base: {formatar_brl(com_base)} | Bônus: {formatar_brl(com_bonus)}",
    )

    st.progress(min(pct_meta / 100.0, 1.0))

    st.divider()

    # Abas funcionais
    aba_lancar, aba_dashboard, aba_metas, aba_historico = st.tabs(
        [
            "➕ Lançar Venda Diária",
            "📈 Gráficos e Evolução 2026",
            "🎯 Configurar Metas",
            "📋 Histórico & Exportar Excel",
        ]
    )

    # ABA 1: Lançamento Diário
    with aba_lancar:
        st.subheader("Novo Lançamento de Venda")
        with st.form("form_nova_venda", clear_on_submit=True):
            col_a, col_b, col_c = st.columns([1, 1, 2])
            data_venda = col_a.date_input("Data da Venda", value=date.today(), min_value=date(2026, 1, 1))
            valor_venda = col_b.number_input("Valor Vendido (R$)", min_value=0.01, step=100.0, format="%.2f")
            obs_venda = col_c.text_input("Observação / Cliente (opcional)", placeholder="Ex: Venda diária")

            if eh_admin:
                usuario_destino = st.selectbox(
                    "Atribuir venda para:",
                    options=["guiadm", "samarete"],
                    format_func=lambda x: USUARIOS[x]["label"],
                )
            else:
                usuario_destino = login

            salvar_btn = st.form_submit_button("Salvar Venda na Nuvem", type="primary")
            if salvar_btn:
                obs_limpa = obs_venda.strip() if obs_venda.strip() else "Lançamento diário"
                if adicionar_venda_firebase(data_venda, usuario_destino, valor_venda, obs_limpa):
                    st.success(
                        f"Venda de {formatar_brl(valor_venda)} salva no Firebase para {USUARIOS[usuario_destino]['nome']}!"
                    )
                    st.rerun()
                else:
                    st.error("Não foi possível salvar no Firebase. Tente novamente.")

    # ABA 2: Gráficos
    with aba_dashboard:
        st.subheader("Desempenho Mensal em 2026 (Realizado vs. Meta)")

        todos_meses_base = sorted(df_m["ano_mes"].unique())
        resumo_mensal = []
        for ym in todos_meses_base:
            v_m = df_v_filtrado[df_v_filtrado["ano_mes"] == ym]["valor"].sum()
            m_m = df_m_filtrado[df_m_filtrado["ano_mes"] == ym]["meta"].sum()
            _, _, c_m = calcular_comissao(v_m, m_m)
            mes_label = f"{NOMES_MESES.get(ym.split('-')[1], ym)}/{ym.split('-')[0][2:]}"
            resumo_mensal.append(
                {
                    "ano_mes": ym,
                    "Mês": mes_label,
                    "Realizado": v_m,
                    "Meta": m_m,
                    "Comissão": c_m,
                }
            )
        df_resumo = pd.DataFrame(resumo_mensal)

        if not df_resumo.empty:
            fig_mensal = go.Figure()
            fig_mensal.add_trace(
                go.Bar(
                    x=df_resumo["Mês"],
                    y=df_resumo["Realizado"],
                    name="Vendas Realizadas (R$)",
                    marker_color="#2E86C1",
                )
            )
            fig_mensal.add_trace(
                go.Scatter(
                    x=df_resumo["Mês"],
                    y=df_resumo["Meta"],
                    name="Meta Mensal (R$)",
                    mode="lines+markers",
                    line=dict(color="#E74C3C", width=3, dash="dash"),
                )
            )
            fig_mensal.update_layout(height=380, hovermode="x unified")
            st.plotly_chart(fig_mensal, use_container_width=True)

            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("#### Evolução das Comissões (R$)")
                fig_com = px.bar(
                    df_resumo,
                    x="Mês",
                    y="Comissão",
                    text_auto=".2f",
                    color_discrete_sequence=["#27AE60"],
                )
                fig_com.update_layout(height=320)
                st.plotly_chart(fig_com, use_container_width=True)

            with col_g2:
                st.markdown(f"#### Vendas Diárias — {mes_selecionado}")
                df_diario = (
                    df_v_filtrado[df_v_filtrado["ano_mes"] == mes_selecionado]
                    .groupby("data", as_index=False)["valor"]
                    .sum()
                    .sort_values("data")
                )
                if not df_diario.empty:
                    fig_dia = px.bar(
                        df_diario,
                        x="data",
                        y="valor",
                        labels={"data": "Dia", "valor": "Vendido (R$)"},
                        color_discrete_sequence=["#8E44AD"],
                    )
                    fig_dia.update_layout(height=320)
                    st.plotly_chart(fig_dia, use_container_width=True)
                else:
                    st.info("Nenhum lançamento neste mês ainda.")

    # ABA 3: Configurar Metas
    with aba_metas:
        st.subheader("Ajustar Metas Mensais")
        if eh_admin:
            usuario_meta = st.selectbox(
                "Selecione o usuário para configurar a meta:",
                options=["guiadm", "samarete"],
                format_func=lambda x: USUARIOS[x]["label"],
            )
        else:
            usuario_meta = login
            st.caption(f"Visualizando metas de: **{USUARIOS[usuario_meta]['label']}**")

        with st.form("form_editar_meta"):
            col_m1, col_m2 = st.columns(2)
            lista_meses = sorted(df_m["ano_mes"].unique())
            mes_edit = col_m1.selectbox(
                "Selecione o Mês",
                options=lista_meses,
                index=lista_meses.index(mes_selecionado) if mes_selecionado in lista_meses else 0,
            )
            valor_atual_meta = df_m[
                (df_m["ano_mes"] == mes_edit) & (df_m["usuario"] == usuario_meta)
            ]["meta"].sum()
            nova_meta = col_m2.number_input(
                "Valor da Meta (R$)",
                min_value=0.0,
                value=float(valor_atual_meta),
                step=5000.0,
                format="%.2f",
            )
            if st.form_submit_button("Atualizar Meta na Nuvem", disabled=not eh_admin):
                if salvar_meta_firebase(mes_edit, usuario_meta, nova_meta):
                    st.success(
                        f"Meta de {mes_edit} salva no Firebase para {USUARIOS[usuario_meta]['nome']}: {formatar_brl(nova_meta)}!"
                    )
                    st.rerun()
                else:
                    st.error("Erro ao salvar meta no Firebase.")

    # ABA 4: Histórico e Exportação
    with aba_historico:
        st.subheader("Histórico de Lançamentos (2026+)")
        df_exibir = df_v_filtrado.sort_values("data", ascending=False).copy()
        df_exibir["Data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")
        df_exibir["Usuário"] = df_exibir["usuario"].map(lambda u: USUARIOS.get(u, {}).get("nome", u))
        df_exibir["Valor (R$)"] = df_exibir["valor"]
        df_exibir["Observação"] = df_exibir["observacao"]

        st.dataframe(
            df_exibir[["Data", "Usuário", "Valor (R$)", "Observação"]],
            use_container_width=True,
            hide_index=True,
        )

        # Exportar para Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_exibir[["Data", "Usuário", "Valor (R$)", "Observação"]].to_excel(
                writer, index=False, sheet_name="Lancamentos_2026"
            )
            if not df_resumo.empty:
                df_resumo[["Mês", "Realizado", "Meta", "Comissão"]].to_excel(
                    writer, index=False, sheet_name="Resumo_Mensal_2026"
                )

        st.download_button(
            label="📥 Baixar Relatório Completo em Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"relatorio_vendas_2026_{date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Opção para excluir um lançamento errado
        if not df_exibir.empty:
            st.divider()
            with st.expander("🗑️ Excluir um lançamento"):
                opcoes_del = {
                    row["id"]: f"{row['Data']} — {row['Usuário']} — {formatar_brl(row['valor'])} ({row['Observação']})"
                    for _, row in df_exibir.iterrows()
                }
                id_para_excluir = st.selectbox(
                    "Selecione o registro para apagar:",
                    options=list(opcoes_del.keys()),
                    format_func=lambda k: opcoes_del[k],
                )
                if st.button("Confirmar Exclusão", type="secondary"):
                    if excluir_venda_firebase(id_para_excluir):
                        st.success("Lançamento removido do Firebase!")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir registro.")


if "usuario_logado" not in st.session_state:
    tela_login()
else:
    app_principal()
