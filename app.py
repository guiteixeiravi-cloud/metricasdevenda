import calendar
import io
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from firebase_db import (
    NOMES_MESES,
    USUARIOS,
    agora_brasil,
    calcular_comissao,
    carregar_dados_firebase,
    excluir_venda_firebase,
    formatar_brl,
    registrar_venda_rapida,
    salvar_meta_firebase,
)
from styles import aplicar_estilo_avancado


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

aplicar_estilo_avancado()


def tela_login():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.15, 1])
    with col2:
        if CAMINHO_LOGO:
            c_img1, c_img2, c_img3 = st.columns([1, 1.3, 1])
            with c_img2:
                st.image(CAMINHO_LOGO, use_container_width=True)

        st.markdown(
            """
            <div style="text-align:center; margin-bottom: 14px;">
                <h2 style="margin:0; color:#f8fafc; font-weight:800;">🔐 Acesso ao Sistema 2026</h2>
                <p style="color:#94a3b8; font-size:0.9rem; margin-top:4px;">
                    Painel Executivo de Vendas, Metas e Comissões
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("form_login"):
            login = st.text_input("Usuário", placeholder="Digite seu usuário").strip().lower()
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            entrar = st.form_submit_button("Entrar no Painel", use_container_width=True)

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

    agora = agora_brasil()
    hoje_str = agora.strftime("%Y-%m-%d")
    hoje_br = agora.strftime("%d/%m/%Y")
    mes_atual_str = agora.strftime("%Y-%m")

    df_v, df_m, conectado_firebase = carregar_dados_firebase()

    # Barra lateral
    with st.sidebar:
        if CAMINHO_LOGO:
            st.image(CAMINHO_LOGO, use_container_width=True)
            st.divider()

        st.markdown(f"### 👤 {info_user['label']}")
        st.caption(f"Perfil: **{'Administrador (Usuário 1)' if eh_admin else 'Vendedora'}**")

        if conectado_firebase:
            st.success("🟢 Firebase sincronizado")
        else:
            st.warning("🟡 Modo offline temporário")

        if st.button("🔄 Atualizar Agora", use_container_width=True):
            st.rerun()

        st.divider()

        if eh_admin:
            filtro_usuario = st.selectbox(
                "Visão do Painel:",
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
        idx_padrao = (
            meses_disponiveis.index(mes_atual_str)
            if mes_atual_str in meses_disponiveis
            else 0
        )

        mes_selecionado = st.selectbox(
            "Mês em Análise (2026+):",
            options=meses_disponiveis,
            index=idx_padrao,
            format_func=lambda ym: f"{NOMES_MESES.get(ym.split('-')[1], ym)}/{ym.split('-')[0]}",
        )

        st.divider()
        if st.button("🚪 Sair", use_container_width=True):
            del st.session_state["usuario_logado"]
            st.rerun()

    # Filtragem dos dados
    if filtro_usuario == "TODOS":
        df_v_filtrado = df_v.copy()
        df_m_filtrado = df_m.copy()
        nome_visao = "Consolidado Geral"
    else:
        df_v_filtrado = df_v[df_v["usuario"] == filtro_usuario].copy()
        df_m_filtrado = df_m[df_m["usuario"] == filtro_usuario].copy()
        nome_visao = USUARIOS[filtro_usuario]["nome"]

    # ==========================================================
    # 1. BANNER SUPERIOR + LANÇAMENTO RÁPIDO (APENAS VALOR)
    # ==========================================================
    col_ban_esq, col_ban_dir = st.columns([1.45, 1], vertical_alignment="center")

    with col_ban_esq:
        c_logo, c_txt = st.columns([0.18, 0.82], vertical_alignment="center")
        with c_logo:
            if CAMINHO_LOGO:
                st.image(CAMINHO_LOGO, use_container_width=True)
        with c_txt:
            status_badge = "🟢 AO VIVO • FIREBASE" if conectado_firebase else "🟡 OFFLINE"
            st.markdown(
                f"""
                <div class="top-banner" style="margin-bottom:0;">
                    <span class="badge-live">{status_badge} • {hoje_br}</span>
                    <div class="welcome-title" style="margin-top:6px;">👋 Bem vindo, {info_user['nome']}</div>
                    <div class="welcome-sub">Exibindo resultados de: <b>{nome_visao}</b> • Referência: <b>{mes_selecionado}</b></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_ban_dir:
        st.markdown(
            """
            <div style="font-size:0.85rem; font-weight:700; color:#f8fafc; margin-bottom:4px;">
                ⚡ Lançar Venda de Hoje (Apenas o Valor)
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("form_venda_rapida", clear_on_submit=True):
            c_val, c_btn = st.columns([1.4, 1], vertical_alignment="bottom")
            valor_rapido = c_val.number_input(
                "Valor da Venda (R$)",
                min_value=0.01,
                value=None,
                step=50.0,
                format="%.2f",
                placeholder="Ex: 1250,00",
                label_visibility="collapsed",
            )
            enviado = c_btn.form_submit_button("➕ Registrar", use_container_width=True)

            if enviado:
                if valor_rapido and valor_rapido > 0:
                    if registrar_venda_rapida(login, float(valor_rapido)):
                        st.toast(f"✅ Venda de {formatar_brl(float(valor_rapido))} registrada!", icon="🚀")
                        st.rerun()
                    else:
                        st.error("Erro ao salvar no Firebase.")
                else:
                    st.warning("Digite o valor da venda.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================================
    # 2. PAINEL DE HOJE (VENDAS DO DIA LOGO AO ABRIR)
    # ==========================================================
    df_hoje = df_v_filtrado[df_v_filtrado["data_str"] == hoje_str].copy()
    total_hoje = df_hoje["valor"].sum() if not df_hoje.empty else 0.0
    qtd_hoje = len(df_hoje)
    ticket_hoje = (total_hoje / qtd_hoje) if qtd_hoje > 0 else 0.0

    # Cálculos do mês selecionado e ritmo diário
    vendido_mes = df_v_filtrado[df_v_filtrado["ano_mes"] == mes_selecionado]["valor"].sum()
    meta_mes = df_m_filtrado[df_m_filtrado["ano_mes"] == mes_selecionado]["meta"].sum()
    com_base, com_bonus, com_total = calcular_comissao(vendido_mes, meta_mes)
    falta_meta = max(0.0, meta_mes - vendido_mes)
    excedente_meta = max(0.0, vendido_mes - meta_mes)
    pct_meta = (vendido_mes / meta_mes * 100) if meta_mes > 0 else 0.0

    ano_sel, mes_sel_num = map(int, mes_selecionado.split("-"))
    dias_no_mes = calendar.monthrange(ano_sel, mes_sel_num)[1]
    if mes_selecionado == mes_atual_str:
        dias_restantes = max(1, dias_no_mes - agora.day + 1)
        dias_passados = max(1, agora.day)
    else:
        dias_restantes = dias_no_mes
        dias_passados = dias_no_mes

    ritmo_necessario = (falta_meta / dias_restantes) if falta_meta > 0 else 0.0
    projecao_mes = (vendido_mes / dias_passados) * dias_no_mes if mes_selecionado == mes_atual_str else vendido_mes

    # Acumulado Anual 2026
    total_ano_2026 = df_v_filtrado["valor"].sum()
    comissao_ano_2026 = 0.0
    for ym_item in df_m_filtrado["ano_mes"].unique():
        v_item = df_v_filtrado[df_v_filtrado["ano_mes"] == ym_item]["valor"].sum()
        m_item = df_m_filtrado[df_m_filtrado["ano_mes"] == ym_item]["meta"].sum()
        _, _, c_item = calcular_comissao(v_item, m_item)
        comissao_ano_2026 += c_item

    st.markdown(f'<div class="section-header">🔥 Resumo & Vendas de Hoje ({hoje_br})</div>', unsafe_allow_html=True)

    col_hoje_kpis, col_hoje_lista = st.columns([1.15, 1.35], gap="medium")

    with col_hoje_kpis:
        hk1, hk2 = st.columns(2)
        with hk1:
            st.markdown(
                f"""
                <div class="kpi-card kpi-accent-green">
                    <div class="kpi-label">Vendido Hoje</div>
                    <div class="kpi-value">{formatar_brl(total_hoje)}</div>
                    <div class="kpi-delta"><span class="delta-pos">{qtd_hoje} venda(s)</span> registrada(s)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with hk2:
            st.markdown(
                f"""
                <div class="kpi-card kpi-accent-blue">
                    <div class="kpi-label">Ticket Médio Hoje</div>
                    <div class="kpi-value">{formatar_brl(ticket_hoje)}</div>
                    <div class="kpi-delta">Média por lançamento</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        hk3, hk4 = st.columns(2)
        with hk3:
            if falta_meta > 0:
                st.markdown(
                    f"""
                    <div class="kpi-card kpi-accent-amber">
                        <div class="kpi-label">Meta Diária Ideal</div>
                        <div class="kpi-value">{formatar_brl(ritmo_necessario)}</div>
                        <div class="kpi-delta">Nos próximos <span class="delta-warn">{dias_restantes} dia(s)</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="kpi-card kpi-accent-green">
                        <div class="kpi-label">Status da Meta</div>
                        <div class="kpi-value">Batida! 🚀</div>
                        <div class="kpi-delta"><span class="delta-pos">+{formatar_brl(excedente_meta)}</span> acima</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        with hk4:
            st.markdown(
                f"""
                <div class="kpi-card kpi-accent-red">
                    <div class="kpi-label">Projeção do Mês</div>
                    <div class="kpi-value">{formatar_brl(projecao_mes)}</div>
                    <div class="kpi-delta">Ritmo atual do período</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_hoje_lista:
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 14px 16px;">
                <div style="font-size:0.85rem; font-weight:700; color:#e2e8f0; margin-bottom:10px;">
                    🧾 Lançamentos Realizados Hoje
                </div>
            """,
            unsafe_allow_html=True,
        )
        if df_hoje.empty:
            st.info("Nenhuma venda registrada hoje ainda. Digite o valor no campo acima para lançar a primeira!")
        else:
            df_hoje_ord = df_hoje.iloc[::-1].copy()
            for _, row in df_hoje_ord.iterrows():
                vend_nome = USUARIOS.get(row["usuario"], {}).get("nome", row["usuario"])
                hora_txt = row.get("hora", "--:--")
                c_item_info, c_item_del = st.columns([0.86, 0.14], vertical_alignment="center")
                with c_item_info:
                    st.markdown(
                        f"""
                        <div class="sale-row">
                            <div>
                                <div class="sale-val">{formatar_brl(row['valor'])}</div>
                                <div class="sale-meta">👤 {vend_nome} • 🕒 {hora_txt} • {row['observacao']}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_item_del:
                    if st.button("🗑️", key=f"del_hoje_{row['id']}", help="Apagar este lançamento"):
                        if excluir_venda_firebase(row["id"]):
                            st.toast("Lançamento removido.")
                            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ==========================================================
    # 3. INDICADORES PRINCIPAIS DO MÊS & ACUMULADO 2026
    # ==========================================================
    st.markdown(f'<div class="section-header">📊 Desempenho Consolidado — {mes_selecionado} & Ano 2026</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-blue">
                <div class="kpi-label">Faturamento no Mês</div>
                <div class="kpi-value">{formatar_brl(vendido_mes)}</div>
                <div class="kpi-delta"><span class="delta-pos">{pct_meta:.1f}%</span> da meta atingida</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        if excedente_meta > 0:
            sub_meta = f'<span class="delta-pos">Superou em {formatar_brl(excedente_meta)} 🚀</span>'
        else:
            sub_meta = f'Falta <span class="delta-warn">{formatar_brl(falta_meta)}</span>'
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-amber">
                <div class="kpi-label">Meta Mensal</div>
                <div class="kpi-value">{formatar_brl(meta_mes)}</div>
                <div class="kpi-delta">{sub_meta}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-label">Comissão Estimada (Mês)</div>
                <div class="kpi-value">{formatar_brl(com_total)}</div>
                <div class="kpi-delta">Base: {formatar_brl(com_base)} | Bônus: {formatar_brl(com_bonus)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-red">
                <div class="kpi-label">Acumulado Total 2026</div>
                <div class="kpi-value">{formatar_brl(total_ano_2026)}</div>
                <div class="kpi-delta">Comissões 2026: <span class="delta-pos">{formatar_brl(comissao_ano_2026)}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    largura_barra = min(pct_meta, 100.0)
    st.markdown(
        f"""
        <div class="prog-wrap">
            <div class="prog-fill" style="width: {largura_barra:.1f}%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#94a3b8; margin-bottom:14px;">
            <span>Progresso da Meta ({mes_selecionado})</span>
            <span><b>{pct_meta:.1f}%</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==========================================================
    # 4. GRÁFICOS INTERATIVOS DIRETO NA DASH PRINCIPAL
    # ==========================================================
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
                "Bateu": v_m >= m_m and m_m > 0,
            }
        )
    df_resumo = pd.DataFrame(resumo_mensal)

    col_graf_1, col_graf_2 = st.columns([1.35, 1], gap="medium")

    with col_graf_1:
        st.markdown('<div class="section-header">📈 Evolução Mensal 2026 (Realizado vs. Meta)</div>', unsafe_allow_html=True)
        if not df_resumo.empty:
            cores_barras = ["#10b981" if b else "#e11d48" for b in df_resumo["Bateu"]]
            fig_mensal = go.Figure()
            fig_mensal.add_trace(
                go.Bar(
                    x=df_resumo["Mês"],
                    y=df_resumo["Realizado"],
                    name="Realizado (R$)",
                    marker_color=cores_barras,
                )
            )
            fig_mensal.add_trace(
                go.Scatter(
                    x=df_resumo["Mês"],
                    y=df_resumo["Meta"],
                    name="Meta (R$)",
                    mode="lines+markers",
                    line=dict(color="#f59e0b", width=3, dash="dash"),
                    marker=dict(size=7),
                )
            )
            fig_mensal.update_layout(
                height=340,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.45)",
                font=dict(color="#e2e8f0"),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_mensal, use_container_width=True)

    with col_graf_2:
        st.markdown(f'<div class="section-header">📅 Vendas Diárias — {mes_selecionado}</div>', unsafe_allow_html=True)
        df_diario = (
            df_v_filtrado[df_v_filtrado["ano_mes"] == mes_selecionado]
            .groupby("data", as_index=False)["valor"]
            .sum()
            .sort_values("data")
        )
        if not df_diario.empty:
            df_diario["Dia"] = df_diario["data"].dt.strftime("%d/%m")
            fig_dia = px.bar(
                df_diario,
                x="Dia",
                y="valor",
                labels={"Dia": "Data", "valor": "Vendido (R$)"},
                color_discrete_sequence=["#3b82f6"],
            )
            fig_dia.update_layout(
                height=340,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.45)",
                font=dict(color="#e2e8f0"),
            )
            st.plotly_chart(fig_dia, use_container_width=True)
        else:
            st.info("Nenhum lançamento neste mês ainda.")

    # ==========================================================
    # 5. HISTÓRICO COMPLETO, METAS E EXPORTAÇÃO NA MESMA TELA
    # ==========================================================
    st.divider()
    col_hist, col_gestao = st.columns([1.5, 1], gap="medium")

    with col_hist:
        st.markdown('<div class="section-header">📋 Histórico Completo de Lançamentos (2026+)</div>', unsafe_allow_html=True)
        df_exibir = df_v_filtrado.sort_values(["data", "hora"], ascending=[False, False]).copy()
        df_exibir["Data"] = df_exibir["data"].dt.strftime("%d/%m/%Y")
        df_exibir["Hora"] = df_exibir["hora"]
        df_exibir["Usuário"] = df_exibir["usuario"].map(lambda u: USUARIOS.get(u, {}).get("nome", u))
        df_exibir["Valor (R$)"] = df_exibir["valor"]
        df_exibir["Observação"] = df_exibir["observacao"]

        st.dataframe(
            df_exibir[["Data", "Hora", "Usuário", "Valor (R$)", "Observação"]],
            use_container_width=True,
            hide_index=True,
            height=260,
        )

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_exibir[["Data", "Hora", "Usuário", "Valor (R$)", "Observação"]].to_excel(
                writer, index=False, sheet_name="Lancamentos_2026"
            )
            if not df_resumo.empty:
                df_resumo[["Mês", "Realizado", "Meta", "Comissão"]].to_excel(
                    writer, index=False, sheet_name="Resumo_Mensal_2026"
                )

        st.download_button(
            label="📥 Exportar Relatório Completo (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"relatorio_vendas_2026_{agora.strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col_gestao:
        st.markdown('<div class="section-header">⚙️ Metas & Gerenciamento</div>', unsafe_allow_html=True)
        if eh_admin:
            with st.expander("🎯 Configurar Metas Mensais", expanded=True):
                with st.form("form_editar_meta"):
                    usuario_meta = st.selectbox(
                        "Usuário:",
                        options=["guiadm", "samarete"],
                        format_func=lambda x: USUARIOS[x]["label"],
                    )
                    lista_meses = sorted(df_m["ano_mes"].unique())
                    mes_edit = st.selectbox(
                        "Mês:",
                        options=lista_meses,
                        index=lista_meses.index(mes_selecionado) if mes_selecionado in lista_meses else 0,
                    )
                    valor_atual_meta = df_m[
                        (df_m["ano_mes"] == mes_edit) & (df_m["usuario"] == usuario_meta)
                    ]["meta"].sum()
                    nova_meta = st.number_input(
                        "Nova Meta (R$):",
                        min_value=0.0,
                        value=float(valor_atual_meta),
                        step=5000.0,
                        format="%.2f",
                    )
                    if st.form_submit_button("Salvar Meta", use_container_width=True):
                        if salvar_meta_firebase(mes_edit, usuario_meta, nova_meta):
                            st.success(f"Meta de {mes_edit} atualizada!")
                            st.rerun()
        else:
            st.info(f"Meta atual de {mes_selecionado}: **{formatar_brl(meta_mes)}**")

        if not df_exibir.empty:
            with st.expander("🗑️ Excluir Lançamento Antigo"):
                opcoes_del = {
                    row["id"]: f"{row['Data']} ({row['Hora']}) — {row['Usuário']} — {formatar_brl(row['valor'])}"
                    for _, row in df_exibir.iterrows()
                }
                id_para_excluir = st.selectbox(
                    "Registro:",
                    options=list(opcoes_del.keys()),
                    format_func=lambda k: opcoes_del[k],
                )
                if st.button("Apagar Registro", use_container_width=True):
                    if excluir_venda_firebase(id_para_excluir):
                        st.success("Registro removido!")
                        st.rerun()


if "usuario_logado" not in st.session_state:
    tela_login()
else:
    app_principal()
