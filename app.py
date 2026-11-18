import calendar
from datetime import date
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


def calcular_calendario_seg_sab(ano: int, mes: int, hoje: date) -> tuple[int, int, int]:
    """Calcula dias comerciais considerando Segunda (0) a Sábado (5), excluindo Domingos (6)."""
    num_dias = calendar.monthrange(ano, mes)[1]
    todas_datas = [date(ano, mes, d) for d in range(1, num_dias + 1)]
    dias_uteis = [d for d in todas_datas if d.weekday() < 6]
    total_uteis = len(dias_uteis)

    ym_sel = f"{ano:04d}-{mes:02d}"
    ym_hoje = hoje.strftime("%Y-%m")

    if ym_sel < ym_hoje:
        passados = total_uteis
        restantes = 0
    elif ym_sel > ym_hoje:
        passados = 0
        restantes = total_uteis
    else:
        passados = max(1, len([d for d in dias_uteis if d <= hoje]))
        restantes = len([d for d in dias_uteis if d >= hoje])

    return total_uteis, passados, restantes


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
    hoje_date = agora.date()
    hoje_str = agora.strftime("%Y-%m-%d")
    hoje_br = agora.strftime("%d/%m/%Y")
    mes_atual_str = agora.strftime("%Y-%m")

    dias_semana_pt = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    nome_dia_hoje = dias_semana_pt[hoje_date.weekday()]

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

    # Calendário comercial Segunda a Sábado (sem domingos)
    ano_sel, mes_sel_num = map(int, mes_selecionado.split("-"))
    dias_uteis_mes, dias_uteis_passados, dias_uteis_restantes = calcular_calendario_seg_sab(
        ano_sel, mes_sel_num, hoje_date
    )

    # ==========================================================
    # 1. BANNER SUPERIOR + LANÇAMENTO RÁPIDO (APENAS VALOR)
    # ==========================================================
    col_ban_esq, col_ban_dir = st.columns([1.45, 1], vertical_alignment="center")

    with col_ban_esq:
        c_logo, c_txt = st.columns([0.17, 0.83], vertical_alignment="center")
        with c_logo:
            if CAMINHO_LOGO:
                st.image(CAMINHO_LOGO, use_container_width=True)
        with c_txt:
            status_badge = "🟢 AO VIVO • FIREBASE" if conectado_firebase else "🟡 OFFLINE"
            st.markdown(
                f"""
                <div class="top-banner" style="margin-bottom:0;">
                    <div>
                        <span class="badge-live">{status_badge} • {nome_dia_hoje}, {hoje_br}</span>
                        <span class="badge-workdays">🗓️ Seg–Sáb: {dias_uteis_passados}/{dias_uteis_mes} dias úteis ({dias_uteis_restantes} restantes)</span>
                    </div>
                    <div class="welcome-title">👋 Bem vindo, {info_user['nome']}</div>
                    <div class="welcome-sub">Visão ativa: <b>{nome_visao}</b> • Período: <b>{mes_selecionado}</b></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_ban_dir:
        st.markdown('<div class="quick-add-box">', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="font-size:0.86rem; font-weight:800; color:#f8fafc; margin-bottom:6px;">
                ⚡ Lançamento Rápido de Hoje (Apenas Valor)
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("form_venda_rapida", clear_on_submit=True):
            c_val, c_btn = st.columns([1.45, 1], vertical_alignment="bottom")
            valor_rapido = c_val.number_input(
                "Valor da Venda (R$)",
                min_value=0.01,
                value=None,
                step=50.0,
                format="%.2f",
                placeholder="Digite o valor (Ex: 450,00)",
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
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================================
    # 2. PAINEL DE HOJE + TERMÔMETRO DIÁRIO (SEG A SÁB)
    # ==========================================================
    df_hoje = df_v_filtrado[df_v_filtrado["data_str"] == hoje_str].copy()
    total_hoje = df_hoje["valor"].sum() if not df_hoje.empty else 0.0
    qtd_hoje = len(df_hoje)
    ticket_hoje = (total_hoje / qtd_hoje) if qtd_hoje > 0 else 0.0

    vendido_mes = df_v_filtrado[df_v_filtrado["ano_mes"] == mes_selecionado]["valor"].sum()
    meta_mes = df_m_filtrado[df_m_filtrado["ano_mes"] == mes_selecionado]["meta"].sum()
    com_base, com_bonus, com_total = calcular_comissao(vendido_mes, meta_mes)
    falta_meta = max(0.0, meta_mes - vendido_mes)
    excedente_meta = max(0.0, vendido_mes - meta_mes)
    pct_meta = (vendido_mes / meta_mes * 100) if meta_mes > 0 else 0.0

    # Cálculos comerciais excluindo domingos
    ritmo_necessario = (
        (falta_meta / dias_uteis_restantes)
        if (falta_meta > 0 and dias_uteis_restantes > 0)
        else 0.0
    )
    media_util_atual = (vendido_mes / dias_uteis_passados) if dias_uteis_passados > 0 else 0.0
    projecao_mes = (
        media_util_atual * dias_uteis_mes
        if mes_selecionado == mes_atual_str
        else vendido_mes
    )
    pct_hoje_vs_meta_dia = (
        (total_hoje / ritmo_necessario * 100)
        if ritmo_necessario > 0
        else (100.0 if total_hoje > 0 else 0.0)
    )

    # Acumulado Anual 2026
    total_ano_2026 = df_v_filtrado["valor"].sum()
    comissao_ano_2026 = 0.0
    for ym_item in df_m_filtrado["ano_mes"].unique():
        v_item = df_v_filtrado[df_v_filtrado["ano_mes"] == ym_item]["valor"].sum()
        m_item = df_m_filtrado[df_m_filtrado["ano_mes"] == ym_item]["meta"].sum()
        _, _, c_item = calcular_comissao(v_item, m_item)
        comissao_ano_2026 += c_item

    st.markdown(f'<div class="section-header">🔥 Operação de Hoje ({nome_dia_hoje}, {hoje_br})</div>', unsafe_allow_html=True)

    col_hoje_kpis, col_hoje_lista = st.columns([1.2, 1.3], gap="medium")

    with col_hoje_kpis:
        hk1, hk2 = st.columns(2)
        with hk1:
            st.markdown(
                f"""
                <div class="kpi-card kpi-accent-green">
                    <div class="kpi-label">Vendido Hoje</div>
                    <div class="kpi-value">{formatar_brl(total_hoje)}</div>
                    <div class="kpi-delta"><span class="delta-pos">{qtd_hoje} entrada(s)</span> hoje • Ticket: {formatar_brl(ticket_hoje)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with hk2:
            if falta_meta > 0 and dias_uteis_restantes > 0:
                st.markdown(
                    f"""
                    <div class="kpi-card kpi-accent-amber">
                        <div class="kpi-label">Meta Diária (Seg–Sáb)</div>
                        <div class="kpi-value">{formatar_brl(ritmo_necessario)}</div>
                        <div class="kpi-delta">Restam <span class="delta-warn">{dias_uteis_restantes} dia(s) úteis</span> s/ domingo</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="kpi-card kpi-accent-green">
                        <div class="kpi-label">Meta Diária (Seg–Sáb)</div>
                        <div class="kpi-value">Concluída! 🏆</div>
                        <div class="kpi-delta">Excedente: <span class="delta-pos">+{formatar_brl(excedente_meta)}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        hk3, hk4 = st.columns(2)
        with hk3:
            st.markdown(
                f"""
                <div class="kpi-card kpi-accent-blue">
                    <div class="kpi-label">Média / Dia Útil</div>
                    <div class="kpi-value">{formatar_brl(media_util_atual)}</div>
                    <div class="kpi-delta">Base: <b>{dias_uteis_passados} dias úteis</b> (Seg–Sáb)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with hk4:
            _, _, com_proj = calcular_comissao(projecao_mes, meta_mes)
            st.markdown(
                f"""
                <div class="kpi-card kpi-accent-purple">
                    <div class="kpi-label">Projeção Fechamento</div>
                    <div class="kpi-value">{formatar_brl(projecao_mes)}</div>
                    <div class="kpi-delta">Comissão proj.: <span class="delta-pos">{formatar_brl(com_proj)}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Termômetro da Meta do Dia
        larg_dia = min(pct_hoje_vs_meta_dia, 100.0)
        st.markdown(
            f"""
            <div class="prog-container">
                <div style="display:flex; justify-content:space-between; font-size:0.82rem; color:#cbd5e1;">
                    <span>🎯 <b>Termômetro de Hoje</b> (Vendido Hoje vs. Meta Diária Seg–Sáb)</span>
                    <span class="delta-pos">{pct_hoje_vs_meta_dia:.1f}%</span>
                </div>
                <div class="prog-wrap">
                    <div class="prog-fill-day" style="width: {larg_dia:.1f}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_hoje_lista:
        st.markdown(
            """
            <div style="background: rgba(15, 23, 42, 0.78); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 16px 18px; height: 100%;">
                <div style="font-size:0.88rem; font-weight:800; color:#f1f5f9; margin-bottom:10px;">
                    🧾 Entradas Registradas Hoje
                </div>
            """,
            unsafe_allow_html=True,
        )
        if df_hoje.empty:
            st.info("Nenhuma venda registrada hoje ainda. Digite apenas o valor lá no topo para somar a primeira!")
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
    # 3. INDICADORES PRINCIPAIS DO MÊS & VELOCÍMETRO DA META
    # ==========================================================
    st.markdown(f'<div class="section-header">📊 Fechamento do Mês ({mes_selecionado}) & Acumulado 2026</div>', unsafe_allow_html=True)

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
                <div class="kpi-label">Comissão Total (Mês)</div>
                <div class="kpi-value">{formatar_brl(com_total)}</div>
                <div class="kpi-delta">0,15%: {formatar_brl(com_base)} | +0,5%: {formatar_brl(com_bonus)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f"""
            <div class="kpi-card kpi-accent-red">
                <div class="kpi-label">Acumulado Anual 2026</div>
                <div class="kpi-value">{formatar_brl(total_ano_2026)}</div>
                <div class="kpi-delta">Comissões 2026: <span class="delta-pos">{formatar_brl(comissao_ano_2026)}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================================
    # 4. GRÁFICOS MODERNOS (GAUGE, SEMANAL, DIÁRIO E ANUAL)
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

    col_g_gauge, col_g_mensal = st.columns([1, 1.55], gap="medium")

    with col_g_gauge:
        st.markdown('<div class="section-header">🎯 Velocímetro da Meta & Bônus 0,5%</div>', unsafe_allow_html=True)
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=pct_meta,
                number={"suffix": "%", "font": {"size": 34, "color": "#f8fafc"}},
                delta={"reference": 100.0, "increasing": {"color": "#10b981"}, "decreasing": {"color": "#f43f5e"}},
                gauge={
                    "axis": {"range": [0, max(130, pct_meta + 10)], "tickcolor": "#94a3b8"},
                    "bar": {"color": "#10b981" if pct_meta >= 100 else "#e11d48"},
                    "bgcolor": "rgba(15,23,42,0.6)",
                    "steps": [
                        {"range": [0, 70], "color": "rgba(225, 29, 72, 0.18)"},
                        {"range": [70, 100], "color": "rgba(245, 158, 11, 0.22)"},
                        {"range": [100, max(130, pct_meta + 10)], "color": "rgba(16, 185, 129, 0.25)"},
                    ],
                    "threshold": {
                        "line": {"color": "#fbbf24", "width": 4},
                        "thickness": 0.8,
                        "value": 100,
                    },
                },
            )
        )
        fig_gauge.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_g_mensal:
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
                height=320,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.45)",
                font=dict(color="#e2e8f0"),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_mensal, use_container_width=True)

    # Segunda linha de gráficos: Diário + Semanal do Mês
    df_mes_atual = df_v_filtrado[df_v_filtrado["ano_mes"] == mes_selecionado].copy()
    col_g_dia, col_g_sem = st.columns([1.35, 1], gap="medium")

    with col_g_dia:
        st.markdown(f'<div class="section-header">📅 Evolução Diária — {mes_selecionado}</div>', unsafe_allow_html=True)
        df_diario = (
            df_mes_atual.groupby("data", as_index=False)["valor"]
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
            if ritmo_necessario > 0:
                fig_dia.add_hline(
                    y=ritmo_necessario,
                    line_dash="dot",
                    line_color="#f59e0b",
                    annotation_text="Meta/Dia (Seg-Sáb)",
                    annotation_position="top left",
                )
            fig_dia.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.45)",
                font=dict(color="#e2e8f0"),
            )
            st.plotly_chart(fig_dia, use_container_width=True)
        else:
            st.info("Nenhum lançamento neste mês ainda.")

    with col_g_sem:
        st.markdown(f'<div class="section-header">📊 Ritmo por Semana — {mes_selecionado}</div>', unsafe_allow_html=True)
        if not df_mes_atual.empty:
            df_mes_atual["Semana"] = df_mes_atual["data"].dt.day.map(
                lambda d: f"Semana {(d - 1) // 7 + 1}"
            )
            df_semanal = (
                df_mes_atual.groupby("Semana", as_index=False)["valor"]
                .sum()
                .sort_values("Semana")
            )
            fig_sem = px.bar(
                df_semanal,
                x="Semana",
                y="valor",
                text_auto=".2s",
                labels={"Semana": "Semana do Mês", "valor": "Total (R$)"},
                color_discrete_sequence=["#a855f7"],
            )
            fig_sem.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.45)",
                font=dict(color="#e2e8f0"),
            )
            st.plotly_chart(fig_sem, use_container_width=True)
        else:
            st.info("Sem dados semanais para este mês.")

    # ==========================================================
    # 5. SIMULADOR DE COMISSÃO + HISTÓRICO & GERENCIAMENTO
    # ==========================================================
    st.divider()
    col_hist, col_gestao = st.columns([1.45, 1.05], gap="medium")

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
            height=270,
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
        st.markdown('<div class="section-header">🧮 Simulador & Configurações</div>', unsafe_allow_html=True)

        with st.expander("💰 Simulador Rápido de Comissão", expanded=True):
            alvo_padrao = float(max(vendido_mes, meta_mes, 150000.0))
            valor_simulado = st.slider(
                "Simular fechamento do mês em (R$):",
                min_value=50000.0,
                max_value=300000.0,
                value=min(300000.0, alvo_padrao),
                step=2500.0,
            )
            s_base, s_bonus, s_tot = calcular_comissao(valor_simulado, meta_mes)
            st.markdown(
                f"""
                <div style="font-size:0.88rem; color:#cbd5e1; line-height:1.6;">
                    • Comissão Base (0,15%): <b>{formatar_brl(s_base)}</b><br>
                    • Bônus Acima da Meta (0,5%): <b style="color:#34d399;">{formatar_brl(s_bonus)}</b><br>
                    • <b>Total a Receber: <span style="color:#fbbf24; font-size:1.05rem;">{formatar_brl(s_tot)}</span></b>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if eh_admin:
            with st.expander("🎯 Configurar Metas Mensais"):
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
