import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# 日本語フォント設定
matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'

st.set_page_config(page_title="スクレーパ摩耗予測", layout="wide")

st.title("スクレーパ押し付け力・摩耗寿命予測アプリ")

# ======= 🌟 サイドバーすべての入力 =======
with st.sidebar:
    st.header("📥 入力パラメータ")

    # 幾何パラメータ
    L_mm = st.number_input("スクレーパ長さ L [mm]", min_value=1.0, value=30.0)
    b_mm = st.number_input("スクレーパ幅 b [mm]", min_value=1.0, value=10.0)
    h_mm = st.number_input("スクレーパ厚さ h [mm]", min_value=0.1, value=3.0)
    E_GPa = st.number_input("ヤング率 E [GPa]", min_value=0.01, value=0.55)
    max_delta_mm = st.number_input("最大変形量 δ_max [mm]", min_value=0.1, value=2.0)

    st.markdown("---")

    # 材料特性選択
    material_options = {
        "PTFE（テフロン）": {"K": 1e-3, "H": 50},
        "ウレタン": {"K": 2e-4, "H": 70},
        "ゴム系（NBR）": {"K": 1e-4, "H": 40},
        "金属（参考）": {"K": 1e-5, "H": 300}
    }
    material = st.selectbox("材料を選択", list(material_options.keys()))
    apply_edge_correction = st.checkbox("C0.3エッジ補正（摩耗係数を1.5倍）", value=True)

    st.markdown("---")

    # 摩耗計算用パラメータ
    s_mm = st.number_input("総移動距離（累積）[mm]", min_value=1.0, value=10000.0)
    move_per_cycle = st.number_input("1chあたりの移動量 [mm]", min_value=0.1, value=100.0)
    V_limit = st.number_input("許容摩耗体積 V_limit [mm³]", min_value=0.1, value=10.0)

# ======= 単位変換と初期計算 =======
L = L_mm / 1000
b = b_mm / 1000
h = h_mm / 1000
E = E_GPa * 1e9
I = (b * h**3) / 12

delta_vals = np.linspace(0, max_delta_mm / 1000, 100)
force_vals = (3 * E * I * delta_vals) / (L**3)
F_latest = force_vals[-1]

# ======= 材料特性読み込み =======
K = material_options[material]["K"]
H = material_options[material]["H"]
if apply_edge_correction:
    K *= 1.5

# ======= 🎨 グラフ =======
st.subheader("📈 押し付け力 vs 変形量")

fig, ax = plt.subplots()
ax.plot(delta_vals * 1000, force_vals, color="blue")
ax.set_xlabel("変形量 δ [mm]")
ax.set_ylabel("押し付け力 F [N]")
ax.set_title("スクレーパ押し付け力 vs 変形量")
ax.grid(True)
st.pyplot(fig, use_container_width=True)

# ======= 📘 異物除去の目安 =======
st.markdown("### 📘 押し付け量と異物除去の目安")
st.markdown("""
| 変形量（mm） | 押し付け力目安（N） | 除去対象の目安              |
|--------------|----------------------|-----------------------------|
| 0.2 mm       | ごく小さい（<0.1N）  | 微粉・ホコリ（軽粉体）       |
| 0.5 mm       | ～0.5N               | 標準的な粉末（アルミ、酸化物など） |
| 1.0 mm       | ～1～2N              | 小粒異物、湿気を含む付着物など |
| 2.0 mm以上    | それ以上             | 強固な付着異物、樹脂破片など   |
""")

# ======= 🛠️ 摩耗計算 =======
st.subheader("🛠️ 摩耗量・寿命予測")

V_wear = (K * F_latest * s_mm) / H
st.write(f"🧮 推定摩耗量: **{V_wear:.3f} mm³**")

if F_latest > 0:
    s_life = (V_limit * H) / (K * F_latest)
    ch_life = s_life / move_per_cycle
    st.success(f"📏 推定寿命距離: **{s_life:,.0f} mm**（= {s_life/1000:.2f} m）")
    st.success(f"🔄 推定寿命: **約 {ch_life:,.0f} ch**（1ch = {move_per_cycle:.1f} mm）")
else:
    st.warning("押し付け力が0 Nのため寿命は無限大と見なされます。")
