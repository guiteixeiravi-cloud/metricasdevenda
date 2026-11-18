import streamlit as st


def aplicar_estilo_avancado():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
            max-width: 1440px;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 12% 8%, rgba(225, 29, 72, 0.12) 0%, transparent 32%),
                radial-gradient(circle at 88% 12%, rgba(59, 130, 246, 0.10) 0%, transparent 35%),
                linear-gradient(180deg, #070b14 0%, #0b1120 55%, #060911 100%);
            color: #f8fafc;
        }

        [data-testid="stHeader"] {
            background: rgba(7, 11, 20, 0.65);
            backdrop-filter: blur(12px);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1324 0%, #070b14 100%);
            border-right: 1px solid rgba(148, 163, 184, 0.12);
        }

        .hero-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.88) 0%, rgba(30, 41, 59, 0.72) 100%);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-left: 4px solid #e11d48;
            border-radius: 18px;
            padding: 20px 24px;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.35);
        }
        .hero-title {
            font-size: 1.6rem;
            font-weight: 800;
            color: #ffffff;
            margin: 6px 0 2px 0;
            letter-spacing: -0.025em;
        }
        .hero-sub {
            font-size: 0.9rem;
            color: #94a3b8;
        }
        .pill-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.14);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.32);
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }
        .pill-calendar {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(59, 130, 246, 0.14);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            margin-left: 6px;
        }

        .quick-box {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.65), rgba(15, 23, 42, 0.88));
            border: 1px solid rgba(225, 29, 72, 0.32);
            border-radius: 18px;
            padding: 16px 20px 10px 20px;
            box-shadow: 0 12px 30px rgba(225, 29, 72, 0.10);
        }
        .quick-title {
            font-size: 0.86rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .kpi-card {
            background: linear-gradient(160deg, rgba(30, 41, 59, 0.68) 0%, rgba(15, 23, 42, 0.90) 100%);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 18px 20px;
            height: 100%;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
            transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
        }
        .kpi-card:hover {
            transform: translateY(-3px);
            border-color:
