import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['font.family'] = 'Noto Sans CJK JP'

st.title("スクレーパ押し付け力 vs 変形量（片持ち梁モデル）")

# 入力部（同じ）

# 計算部（同じ）

# グラフ表示
fig, ax = plt.subplots()
ax.plot(delta_vals * 1000, force_vals, label="押し付け力")
ax.set_xlabel("変形量 δ [mm]")
ax.set_ylabel("押し付け力 F [N]")
ax.set_title("スクレーパ押し付け力 vs 変形量")
ax.grid(True)
st.pyplot(fig)

# 除去対象の目安表示
st.markdown("### 📘 押し付け量と異物除去の目安")
st.markdown("""
| 変形量（mm） | 押し付け力目安（N） | 除去対象の目安              |
|--------------|----------------------|-----------------------------|
| 0.2 mm       | ごく小さい（<0.1N）  | 微粉・ホコリ（軽粉体）       |
| 0.5 mm       | ～0.5N               | 標準的な粉末（アルミ、酸化物など） |
| 1.0 mm       | ～1～2N              | 小粒異物、湿気を含む付着物など |
| 2.0 mm以上    | それ以上             | 強固な付着異物、樹脂破片など   |
""")
