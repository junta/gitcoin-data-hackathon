
import streamlit as st
#import seaborn as sns
import pandas as pd
# import matplotlib.pyplot as plt

st.markdown("# Gitcoin Open Data Science Hackathon")
st.sidebar.markdown("# Gitcoin Open Data Science Hackathon")

st.markdown("""
[Github Repo](https://github.com/junta/gitcoin-data-hackathon)

[Dune Dashboard](https://dune.com/junta8918/gr15)

Official links:

[https://gitcoin.co/hackathon/datascience](https://gitcoin.co/hackathon/datascience)

[Gitcoin Grants Round 15: Round Results & Recap](https://go.gitcoin.co/blog/gr15-results#ecosystem)
""")




# contributions = pd.read_csv('../GR15_public_hackathon/hackathon-contributions-dataset_v2.csv') 
# describe = contributions.groupby(['chain'])['amount_in_usdt'].describe()

# st.table(describe)

# fig, ax = plt.subplots()
# ax.hist(contributions[contributions['amount_in_usdt'] < 20]['amount_in_usdt'], bins=20)
# st.pyplot(fig)