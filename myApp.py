
import streamlit as st
#import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

st.write("""
# Sybil Slayer Bounties
Gitcoin Open Data Science Hackathon
""")

contributions = pd.read_csv('./GR15_public_hackathon/hackathon-contributions-dataset_v2.csv') 
describe = contributions.groupby(['chain'])['amount_in_usdt'].describe()

st.table(describe)

fig, ax = plt.subplots()
ax.hist(contributions[contributions['amount_in_usdt'] < 20]['amount_in_usdt'], bins=20)
st.pyplot(fig)