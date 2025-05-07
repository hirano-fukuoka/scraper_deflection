import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# 日本語フォント設定
matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'

st.set_page_config(page_title="スクレーパ摩耗寿命予測", layout="wide")
st.title("スクレーパ押し付け力・摩耗寿命予測アプリ（押し付け力 < 0.1Nが寿命）")

# ====== 入力（全てサイドバー） ======
with st.sidebar:
    st.header("📥 スクレーパ条件")

    # 寸法
    b_mm = st.number_input("スクレーパ長さ L [mm]", min_value=1.0, value=140.0)
    L_mm = st.number_input("スクレーパ幅 b [mm]", min_value=1.0, value=20.0)
    h_mm = st.number_input("スクレーパ厚さ h [mm]", min_value=0.1, value=1.5)
    E_GPa = st.number_input("ヤング率 E [GPa]", min_value=0.01, value=0.55)
    max_delta_mm = st.number_input("最大変形量 δ_max [mm]", min_value=0.01, value=0.5)

    st.markdown("---")

    # 材料
    material_options = {
        "PTFE（テフロン）": {"K": 1e-3, "H": 50},
        "ウレタン": {"K": 2e-4, "H": 70},
        "ゴム系（NBR）": {"K": 1e-4, "H": 40}
    }
    material = st.selectbox("材料を選択", list(material_options.keys()))
    apply_edge_correction = st.checkbox("C0.3エッジ補正（摩耗係数 ×1.5）", value=True)

    st.markdown("---")

    s_mm = st.number_input("総移動距離の仮定値 [mm]", min_value=1.0, value=10000.0)
    move_per_cycle = st.number_input("1chあたりの移動量 [mm]", min_value=0.1, value=2000.0)

# ====== 単位変換・初期定義 ======
L = L_mm / 1000
b = b_mm / 1000
h = h_mm / 1000
E = E_GPa * 1e9
delta = max_delta_mm / 1000
I = (b * h**3) / 12

# ====== 初期押し付け力（F0） ======
F0 = (3 * E * I * delta) / (L**3)

# ====== 押し付け力0.5Nになる摩耗厚さの計算 ======
F_limit = 0.5
if F0 > F_limit:
    h_new = h * (F_limit / F0) ** (1/3)
    delta_h = h - h_new
    V_limit = L * b * delta_h * 1e9  # m³ → mm³
else:
    h_new = h
    delta_h = 0
    V_limit = 0

# ====== 材料特性読み込み ======
K = material_options[material]["K"]
H = material_options[material]["H"]
if apply_edge_correction:
    K *= 1.5

# ====== 摩耗量と寿命計算 ======
V_wear = (K * F0 * s_mm) / H
if V_limit > 0:
    s_life = (V_limit * H) / (K * F0)
    ch_life = s_life / move_per_cycle
else:
    s_life = float('inf')
    ch_life = float('inf')

# ====== グラフ表示 ======
st.subheader("📈 初期押し付け力 vs 厚み")
st.write(f"📌 初期押し付け力: **{F0:.3f} N**")
st.write(f"📉 厚さが約 **{delta_h*1000:.3f} mm** 減少すると、押し付け力が 0.5N に低下します。")

# ====== 除去能力の参考表示 ======
st.markdown("### 📘 押し付け力と除去能力の参考")
st.markdown("""
| 押し付け力 (N) | 除去対象の目安                         |
|----------------|----------------------------------------|
| < 0.1          | 微粉・ホコリなどの軽微な粉体           |
| 0.1 - 0.5      | 標準的な粉末（酸化物、アルミ粉など）     |
| 0.5 - 2.0      | 小粒な異物、湿気を含んだ付着物           |
| > 2.0          | 固着物、硬質異物（樹脂片、金属粉など）   |
""")

# ====== 摩耗・寿命出力 ======
st.subheader("🛠️ 摩耗寿命予測")
st.write(f"📏 摩耗限界体積: **{V_limit:.3f} mm³**")
st.write(f"📊 摩耗量（仮定移動距離 s = {s_mm:,.0f} mm）: **{V_wear:.3f} mm³**")

if np.isfinite(s_life):
    st.success(f"📏 推定寿命距離: {s_life:,.0f} mm（= {s_life/1000:.2f} m）")
    st.success(f"🔄 推定寿命: 約 {ch_life:,.0f} ch（1ch = {move_per_cycle:.1f} mm）")
else:
    st.warning("押し付け力がすでに 0.5N 以下です。寿命条件に達しています。")
