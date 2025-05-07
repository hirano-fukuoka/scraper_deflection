import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import io
from scipy.optimize import minimize_scalar

# 日本語フォント設定
matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'

st.set_page_config(page_title="スクレーパ摩耗寿命予測", layout="wide")
st.title("スクレーパ押し付け力・摩耗寿命予測アプリ（押し付け力が指定値を下回ると寿命）")

# ====== 入力（全てサイドバー） ======
with st.sidebar:
    st.header("📥 スクレーパ条件")

    L_mm = st.number_input("スクレーパ幅 b [mm]（たわみ方向）", min_value=1.0, value=20.0)
    b_mm = st.number_input("スクレーパ長さ L [mm]（固定長）", min_value=1.0, value=140.0)
    h_mm = st.number_input("スクレーパ厚さ h [mm]", min_value=0.1, value=1.5)
    E_GPa = st.number_input("ヤング率 E [GPa]", min_value=0.01, value=0.55)
    max_delta_mm = st.number_input("最大変形量 δ_max [mm]", min_value=0.1, value=0.5)

    st.markdown("---")

    material_options = {
        "PTFE（テフロン）": {"K": 1e-3, "H": 50},
        "ウレタン": {"K": 2e-4, "H": 70},
        "ゴム系（NBR）": {"K": 1e-4, "H": 40}
    }
    material = st.selectbox("材料を選択", list(material_options.keys()))
    apply_edge_correction = st.checkbox("C0.3エッジ補正（摩耗係数 ×1.5）", value=True)

    st.markdown("---")

    s_mm = st.number_input("総移動距離の仮定値 [mm]", min_value=1.0, value=10000.0)
    move_per_cycle = st.number_input("1chあたりの移動量 [mm]", min_value=0.1, value=100.0)
    F_limit = st.number_input("押し付け力の下限値 [N]", min_value=0.01, value=0.1)

# ====== 定数定義 ======
L = L_mm / 1000
b = b_mm / 1000
h = h_mm / 1000
E = E_GPa * 1e9
I = (b * h**3) / 12
K = material_options[material]["K"]
H = material_options[material]["H"]
if apply_edge_correction:
    K *= 1.5

# ====== 最適化：押し付け力最大寿命探索 ======
def compute_life(delta):
    delta = max(delta, 1e-6)  # avoid zero
    F = (3 * E * I * delta) / (L**3)
    if F <= F_limit:
        return -1e-6
    h_new = h * (F_limit / F) ** (1/3)
    delta_h = h - h_new
    V_limit = L * b * delta_h * 1e9
    if V_limit <= 0:
        return -1e-6
    s_life = (V_limit * H) / (K * F)
    return -s_life

# === 安全ガード：最大変形量が極端に小さい場合は最適化をスキップ ===
if max_delta_mm / 1000 > 0.001:
    opt_result = minimize_scalar(compute_life, bounds=(0.001, max_delta_mm / 1000), method='bounded')
    opt_delta = opt_result.x
    opt_F = (3 * E * I * opt_delta) / (L**3)
    h_new_opt = h * (F_limit / opt_F) ** (1/3)
    delta_h_opt = h - h_new_opt
    V_limit_opt = L * b * delta_h_opt * 1e9
    s_life_opt = (V_limit_opt * H) / (K * opt_F)
    ch_life_opt = s_life_opt / move_per_cycle
else:
    opt_delta = opt_F = delta_h_opt = V_limit_opt = s_life_opt = ch_life_opt = float('nan')

st.subheader("🎯 寿命を最大化する最適押し付け量")
if np.isnan(opt_F):
    st.warning("※ 最大変形量が小さすぎるため最適化計算はスキップされました。")
else:
    st.write(f"🔧 最適たわみ量: **{opt_delta*1000:.3f} mm**")
    st.write(f"🔧 最適押し付け力: **{opt_F:.3f} N**")
    st.success(f"🧭 最大寿命距離: {s_life_opt:,.0f} mm ≈ {s_life_opt/1000:.2f} m")
    st.success(f"🧭 最大寿命: 約 {ch_life_opt:,.0f} ch")
