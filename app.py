import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("スクレーパ押し付け力 vs 変形量（片持ち梁モデル）")

# 入力
L_mm = st.number_input("スクレーパ長さ L [mm]", min_value=1.0, value=30.0)
b_mm = st.number_input("スクレーパ幅 b [mm]", min_value=1.0, value=10.0)
h_mm = st.number_input("スクレーパ厚さ h [mm]", min_value=0.1, value=3.0)
E_GPa = st.number_input("ヤング率 E [GPa]", min_value=0.01, value=0.5)
max_delta_mm = st.number_input("最大変形量 δ_max [mm]", min_value=0.1, value=5.0)

# 単位変換
L = L_mm / 1000
b = b_mm / 1000
h = h_mm / 1000
E = E_GPa * 1e9

# 断面2次モーメント
I = (b * h**3) / 12

# 変形量と対応する押し付け力計算
delta_vals = np.linspace(0, max_delta_mm / 1000, 100)
force_vals = (3 * E * I * delta_vals) / (L**3)

# グラフ表示
fig, ax = plt.subplots()
ax.plot(delta_vals * 1000, force_vals, label="押し付け力")
ax.set_xlabel("変形量 δ [mm]")
ax.set_ylabel("押し付け力 F [N]")
ax.set_title("スクレーパの押し付け力 vs 変形量")
ax.grid(True)
st.pyplot(fig)
