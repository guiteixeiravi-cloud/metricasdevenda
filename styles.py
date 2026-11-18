import streamlit as st


def aplicar_estilo_avancado():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 12% 8%, rgba(225, 29, 72, 0.14) 0%, transparent 35%),
                radial-gradient(circle at 88% 15%, rgba(59, 130, 246, 0.12) 0%, transparent 40%),
                linear-gradient(180deg, #07090e 0%, #0b0f19 50%, #06080f 100%);
            color: #f8fafc;
        }

        [data-testid="stHeader"] {
            background: rgba(7, 9, 14, 0.65);
            backdrop-filter: blur(12px);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #070a12 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.07);
        }

        .top-banner {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.72) 0%, rgba(15, 23, 42, 0.88) 100%);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-left: 5px solid #e11d48;
            border-radius: 18px;
            padding: 20px 24px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
        }
        .welcome-title {
            font-size: 1.7rem;
            font-weight: 800;
            background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 4px 0 2px 0;
            letter-spacing: -0.02em;
        }
        .welcome-sub {
            font-size: 0.9rem;
            color: #94a3b8;
        }
        .badge-live {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.14);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.35);
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.03em;
        }
        .badge-workdays {
            display: inline-flex;
            align-items: center;
            background: rgba(59, 130, 246, 0.14);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.35);
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-left: 6px;
        }

        .quick-add-box {
            background: linear-gradient(145deg, rgba(225, 29, 72, 0.12) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid rgba(225, 29, 72, 0.35);
            border-radius: 16px;
            padding: 14px 18px;
            box-shadow: 0 8px 24px rgba(225, 29, 72, 0.12);
        }

        .kpi-card {
            background: linear-gradient(155deg, rgba(30, 41, 59, 0.65) 0%, rgba(15, 23, 42, 0.9) 100%);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 18px 20px;
            height: 100%;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
            transition: all 0.2s ease;
        }
        .kpi-card:hover {
            border-color: rgba(255, 255, 255, 0.22);
            transform: translateY(-3px);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4);
        }
        .kpi-accent-red { border-top: 3px solid #f43f5e; }
        .kpi-accent-green { border-top: 3px solid #10b981; }
        .kpi-accent-blue { border-top: 3px solid #3b82f6; }
        .kpi-accent-amber { border-top: 3px solid #f59e0b; }
        .kpi-accent-purple { border-top: 3px solid #a855f7; }

        .kpi-label {
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: #94a3b8;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 1.6rem;
            font-weight: 800;
            color: #f8fafc;
            line-height: 1.15;
            letter-spacing: -0.02em;
        }
        .kpi-delta {
            font-size: 0.81rem;
            margin-top: 8px;
            color: #cbd5e1;
        }
        .delta-pos { color: #34d399; font-weight: 700; }
        .delta-warn { color: #fbbf24; font-weight: 700; }
        .delta-red { color: #fb7185; font-weight: 700; }

        .section-header {
            font-size: 1.15rem;
            font-weight: 800;
            color: #f8fafc;
            margin: 12px 0 14px 0;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: -0.01em;
        }

        .prog-container {
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 14px 18px;
            margin: 12px 0;
        }
        .prog-wrap {
            background: rgba(255, 255, 255, 0.07);
            border-radius: 999px;
            height: 12px;
            width: 100%;
            overflow: hidden;
            margin: 8px 0 4px 0;
        }
        .prog-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #e11d48 0%, #f59e0b 50%, #10b981 100%);
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.45);
            transition: width 0.4s ease;
        }
        .prog-fill-day {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 50%, #10b981 100%);
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.45);
            transition: width 0.4s ease;
        }

        .sale-row {
            background: linear-gradient(90deg, rgba(30, 41, 59, 0.65) 0%, rgba(15, 23, 42, 0.5) 100%);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-left: 3px solid #10b981;
            border-radius: 12px;
            padding: 10px 14px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .sale-val {
            font-size: 1.08rem;
            font-weight: 800;
            color: #34d399;
        }
        .sale-meta {
            font-size: 0.8rem;
            color: #94a3b8;
        }

        div.stButton > button[kind="primary"],
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
            color: white;
            border: none;
            font-weight: 700;
            border-radius: 10px;
            padding: 0.55rem 1.2rem;
            box-shadow: 0 4px 15px rgba(225, 29, 72, 0.4);
            transition: all 0.2s ease;
        }
        div.stButton > button[kind="primary"]:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
            transform: translateY(-1px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
