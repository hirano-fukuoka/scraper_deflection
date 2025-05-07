import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# フォント設定（日本語対応）
matplotlib.rcParams['font.family'] = 'MS Gothic'

st.title("スクレーパ押し付け力 vs 変形量（片持ち梁モデル）")

# 🔧 入力
L_mm = st.number_input("スクレーパ長さ L [mm]", min_value=1.0, value=30.0)
b_mm = st.number_input("スクレーパ幅 b [mm]", min_value=1.0, value=10.0)
h_mm = st.number_input("スクレーパ厚さ h [mm]", min_value=0.1, value=3.0)
E_GPa = st.number_input("ヤング率 E [GPa]", min_value=0.01, value=0.55)
max_delta_mm = st.number_input("最大変形量 δ_max [mm]", min_value=0.1, value=1.0)

# 単位変換
L = L_mm / 1000
b = b_mm / 1000
h = h_mm / 1000
E = E_GPa * 1e9

# 📐 断面二次モーメント
I = (b * h**3) / 12

# 📈 データ計算
delta_vals = np.linspace(0, max_delta_mm / 1000, 100)  # 変形量[m]
force_vals = (3 * E * I * delta_vals) / (L**3)         # 力[N]

# 📊 グラフ表示
fig, ax = plt.subplots()
ax.plot(delta_vals * 1000, force_vals, label="押し付け力")  # mm表示
ax.set_xlabel("変形量 δ [mm]")
ax.set_ylabel("押し付け力 F [N]")
ax.set_title("スクレーパ押し付け力 vs 変形量")
ax.grid(True)
st.pyplot(fig)

# 📘 異物除去の目安
st.markdown("### 📘 押し付け量と異物除去の目安")
st.markdown("""
| 変形量（mm） | 押し付け力目安（N） | 除去対象の目安              |
|--------------|----------------------|-----------------------------|
| 0.2 mm       | ごく小さい（<0.1N）  | 微粉・ホコリ（軽粉体）       |
| 0.5 mm       | ～0.5N               | 標準的な粉末（アルミ、酸化物など） |
| 1.0 mm       | ～1～2N              | 小粒異物、湿気を含む付着物など |
| 2.0 mm以上    | それ以上             | 強固な付着異物、樹脂破片など   |
""")
