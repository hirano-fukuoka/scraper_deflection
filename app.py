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

    b_mm = st.number_input("スクレーパ幅 b [mm]（たわみ方向）", min_value=1.0, value=20.0)
    L_mm = st.number_input("スクレーパ長さ L [mm]（固定長）", min_value=1.0, value=140.0)
    h_mm = st.number_input("スクレーパ厚さ h [mm]", min_value=0.1, value=1.5)
    # 材料選択と自動ヤング率設定
    material_options = {
        "PTFE（テフロン）": {"K": 1e-3, "H": 50, "E": 0.55},
        "ウレタン": {"K": 2e-4, "H": 70, "E": 0.025},
        "ゴム系（NBR）": {"K": 1e-4, "H": 40, "E": 0.01}
    }
    material = st.selectbox("材料を選択", list(material_options.keys()))
    default_E = material_options[material]["E"]
    E_GPa = st.number_input("ヤング率 E [GPa]", min_value=0.01, value=default_E)
    max_delta_mm = st.number_input("最大変形量 δ_max [mm]", min_value=0.1, value=0.5)

    st.markdown("---")

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
    delta = max(delta, 1e-6)
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

# ====== 通常計算（入力変形量） ======
delta = max_delta_mm / 1000
F0 = (3 * E * I * delta) / (L**3)

if F0 > F_limit:
    h_new = h * (F_limit / F0) ** (1/3)
    delta_h = h - h_new
    V_limit = L * b * delta_h * 1e9
else:
    h_new = h
    delta_h = 0
    V_limit = 0

V_wear = (K * F0 * s_mm) / H
if V_limit > 0:
    s_life = (V_limit * H) / (K * F0)
    ch_life = s_life / move_per_cycle
else:
    s_life = float('inf')
    ch_life = float('inf')

# ====== 結果表示 ======
st.subheader("📈 初期押し付け力と摩耗予測")
st.write(f"初期押し付け力: **{F0:.3f} N**")
st.write(f"許容摩耗厚さ: **{delta_h * 1000:.3f} mm**")
st.write(f"許容摩耗体積: **{V_limit:.3f} mm³**")
st.write(f"総移動距離 {s_mm:.0f} mm に対する摩耗量: **{V_wear:.3f} mm³**")

if np.isfinite(s_life):
    st.success(f"推定寿命距離: **{s_life:,.0f} mm** （{s_life / 1000:.2f} m）")
    st.success(f"推定寿命: **{ch_life:,.0f} ch**（1ch = {move_per_cycle:.1f} mm）")
else:
    st.warning(f"初期押し付け力が下限（{F_limit:.2f} N）を下回っています。すでに寿命条件に達しています。")

# ====== 最適たわみ量による最大寿命 ======
st.subheader("🎯 寿命最大化のための最適たわみ量")
if np.isnan(opt_F):
    st.warning("最大たわみ量が小さすぎるため、最適化を実行できません。")
else:
    st.write(f"最適たわみ量: **{opt_delta * 1000:.3f} mm**")
    st.write(f"最適押し付け力: **{opt_F:.3f} N**")
    st.success(f"最大寿命距離: **{s_life_opt:,.0f} mm** （{s_life_opt / 1000:.2f} m）")
    st.success(f"最大寿命: **{ch_life_opt:,.0f} ch**")

# ====== グラフ描画：たわみ量 vs 押し付け力、寿命 ======
st.subheader("📊 Deflection vs Contact Force")
delta_vals = np.linspace(0.001, max_delta_mm, 100) / 1000
force_vals = (3 * E * I * delta_vals) / (L**3)

fig, ax = plt.subplots()
ax.plot(delta_vals * 1000, force_vals, label="Contact Force F [N]", color='blue')
ax.axhline(F_limit, color='red', linestyle='--', label="Force Limit")
ax.set_xlabel("Deflection δ [mm]")
ax.set_ylabel("Contact Force F [N]")
ax.grid(True)
ax.legend()
st.pyplot(fig)

st.subheader("📈 Deflection vs Wear Life")
s_life_curve = []
for d in delta_vals:
    F = (3 * E * I * d) / (L**3)
    if F <= F_limit:
        s_life_curve.append(0)
    else:
        h_tmp = h * (F_limit / F)**(1/3)
        delta_h_tmp = h - h_tmp
        V_limit_tmp = L * b * delta_h_tmp * 1e9
        if V_limit_tmp <= 0:
            s_life_curve.append(0)
        else:
            s_life_tmp = (V_limit_tmp * H) / (K * F)
            s_life_curve.append(s_life_tmp)

fig2, ax2 = plt.subplots()
ax2.plot(delta_vals * 1000, s_life_curve, label="Wear Life [mm]", color='green')
ax2.set_xlabel("Deflection δ [mm]")
ax2.set_ylabel("Wear Life Distance [mm]")
ax2.grid(True)
ax2.legend()
st.pyplot(fig2)

st.subheader("📈 Contact Force vs Wear Life")
force_vals_valid = []
s_life_force_curve = []
for d in delta_vals:
    F = (3 * E * I * d) / (L**3)
    if F <= F_limit:
        continue
    h_tmp = h * (F_limit / F)**(1/3)
    delta_h_tmp = h - h_tmp
    V_limit_tmp = L * b * delta_h_tmp * 1e9
    if V_limit_tmp <= 0:
        continue
    s_life_tmp = (V_limit_tmp * H) / (K * F)
    force_vals_valid.append(F)
    s_life_force_curve.append(s_life_tmp)

fig3, ax3 = plt.subplots()
ax3.plot(force_vals_valid, s_life_force_curve, label="Wear Life [mm]", color='purple')
ax3.set_xlabel("Contact Force F [N]")
ax3.set_ylabel("Wear Life Distance [mm]")
ax3.grid(True)
ax3.legend()
st.pyplot(fig3)

# ====== テキスト出力 ======
st.subheader("📄 結果をテキストで出力")
text_output = io.StringIO()
text_output.write("【摩耗寿命予測結果】\\n")
text_output.write(f"材質: {material}\\n")
text_output.write(f"初期押し付け力: {F0:.3f} N\\n")
text_output.write(f"許容摩耗厚さ: {delta_h*1000:.3f} mm\\n")
text_output.write(f"許容摩耗体積: {V_limit:.3f} mm³\\n")
text_output.write(f"総移動距離 {s_mm} mm における摩耗量: {V_wear:.3f} mm³\\n")
text_output.write(f"推定寿命距離: {s_life:,.0f} mm ({s_life/1000:.2f} m)\\n")
text_output.write(f"推定寿命: {ch_life:,.0f} ch\\n")
text_output.write("【最適条件】\\n")
text_output.write(f"最適たわみ量: {opt_delta*1000:.3f} mm\\n")
text_output.write(f"最適押し付け力: {opt_F:.3f} N\\n")
text_output.write(f"最大寿命距離: {s_life_opt:,.0f} mm ({s_life_opt/1000:.2f} m)\\n")
text_output.write(f"最大寿命: {ch_life_opt:,.0f} ch\\n")

st.download_button(


    label="📥 結果を .txt でダウンロード",
    data=text_output.getvalue(),
    file_name="scraper_life_result.txt",
    mime="text/plain"
)
    
