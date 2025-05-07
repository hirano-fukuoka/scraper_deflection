import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# 日本語フォントの設定（Streamlit Cloudでは 'Noto Sans CJK JP' 推奨）
matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'

st.title("スクレーパの押し付け力・摩耗予測アプリ")

# 入力：形状・材料
st.sidebar.header("スクレーパパラメータ設定")

L_mm = st.sidebar.number_input("スクレーパ長さ L [mm]", min_value=1.0, value=30.0)
b_mm = st.sidebar.number_input("スクレーパ幅 b [mm]", min_value=1.0, value=10.0)
h_mm = st.sidebar.number_input("スクレーパ厚さ h [mm]", min_value=0.1, value=3.0)
E_GPa = st.sidebar.number_input("ヤング率 E [GPa]", min_value=0.01, value=0.55)
max_delta_mm = st.sidebar.number_input("最大変形量 δ_max [mm]", min_value=0.1, value=2.0)

# 単位変換
L = L_mm / 1000
b = b_mm / 1000
h = h_mm / 1000
E = E_GPa * 1e9
I = (b * h**3) / 12  # 断面2次モーメント

# 押し付け力 vs 変形量 計算
delta_vals = np.linspace(0, max_delta_mm / 1000, 100)
force_vals = (3 * E * I * delta_vals) / (L**3)

# グラフ表示
st.header("📈 押し付け力 vs 変形量")

fig, ax = plt.subplots()
ax.plot(delta_vals * 1000, force_vals, label="押し付け力")
ax.set_xlabel("変形量 δ [mm]")
ax.set_ylabel("押し付け力 F [N]")
ax.set_title("スクレーパ押し付け力 vs 変形量")
ax.grid(True)
st.pyplot(fig)

# 押し付け量の目安表
st.markdown("### 📘 押し付け量と異物除去の目安")
st.markdown("""
| 変形量（mm） | 押し付け力目安（N） | 除去対象の目安              |
|--------------|----------------------|-----------------------------|
| 0.2 mm       | ごく小さい（<0.1N）  | 微粉・ホコリ（軽粉体）       |
| 0.5 mm       | ～0.5N               | 標準的な粉末（アルミ、酸化物など） |
| 1.0 mm       | ～1～2N              | 小粒異物、湿気を含む付着物など |
| 2.0 mm以上    | それ以上             | 強固な付着異物、樹脂破片など   |
""")

# 摩耗計算セクション
st.header("🛠️ 摩耗量と寿命予測")

# 材料選択
material_options = {
    "PTFE（テフロン）": {"K": 1e-3, "H": 50},
    "ウレタン": {"K": 2e-4, "H": 70},
    "ゴム系（NBR）": {"K": 1e-4, "H": 40},
    "金属（参考）": {"K": 1e-5, "H": 300}
}
material = st.selectbox("材料を選択", list(material_options.keys()))
K = material_options[material]["K"]
H = material_options[material]["H"]

st.write(f"選択された材料：**{material}**")
st.write(f"摩耗係数 K = `{K}`, 材料硬さ H = `{H} MPa`")

# 入力：移動距離
s_mm = st.number_input("スクレーパの移動距離 [mm]", min_value=1.0, value=10000.0)

# 最大押し付け力（終端変形時）
F_latest = force_vals[-1]

# 摩耗量（Archardの法則）
V_wear = (K * F_latest * s_mm) / H
st.write(f"🧮 推定摩耗量: **{V_wear:.3f} mm³**")

# 摩耗寿命予測
V_limit = st.number_input("許容摩耗体積 V_limit [mm³]", min_value=0.1, value=10.0)
if F_latest > 0:
    s_life = (V_limit * H) / (K * F_latest)
    st.success(f"📏 推定寿命距離: **{s_life:,.0f} mm**（= {s_life/1000:.2f} m）")
else:
    st.warning("押し付け力が0 Nのため寿命は無限大と見なされます。")
