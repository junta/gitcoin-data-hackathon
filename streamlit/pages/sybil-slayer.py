
import streamlit as st
#import seaborn as sns
import pandas as pd
# import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ttest_ind, mannwhitneyu

@st.cache
def get_passports():
    return pd.read_csv('./passport/output.csv')

@st.cache
def get_grants_stamps():
    return pd.read_csv('./analytics_data/grants_stamps.csv')

@st.cache
def get_grants_by_ratio():
    return pd.read_csv('./analytics_data/grants_by_ratio.csv')

@st.cache
def get_top50():
    return pd.read_csv('./analytics_data/top.csv')

st.markdown("# Sybil Slayer Bounties")
st.sidebar.markdown("# Sybil Slayer Bounties")

st.write("""
We focused on one type of sybil, attackers(not farmers) and analyzied their behaivior combined with Gitcoin Passport data.
We categorized each grant into three category by stamp_holders_ratio, and 
observed difference among them.
""")

st.markdown("""
    table of contents:
    1. Introduction and hypothesis
    2. Overview of Gitcoin Passport data
    3. Analysis through stamp_holders_ratio
    4. Summary & Proposals
""")

st.subheader("1. Introduction and hypothesis")
st.markdown("""
Attackers cheat on Quadratic Funding sysmte and want to maximize its impact for their project.

We assume their characteristics and behaivior are as follows.
- Have many small amount contributions and average contribution amount is lower than others.
- Have more contributors compared to projects received similar amount of donations. (They created lots of sock puppet accounts)
- May collect passport stamps if they highly motivated(to get Trust Bonus and maximize impact), but some of them don't do because it is time-consuming work.
Those are valid reasoning, given how the QF system works.
""")

st.subheader("2. Overview of Gitcoin Passport data")
st.markdown("""
We gathered Gitcoin Passport data of each contributors in Round 15 by [Gitcoin Passport SDK: Reader](https://github.com/gitcoinco/passport-sdk/tree/main/packages/reader).

And filtered their stamps to valid stamps as issuanceDate is before 2022-09-23(the last day of GR15) and not expired yet.
""")

passport = get_passports()

non_hodler_count = passport[passport['valid_stamps_count'] == 0.0].count()['address']
holders_count = passport[passport['valid_stamps_count'] != 0.0].count()['address']
holders = passport[passport['valid_stamps_count'] != 0.0]

holders_str = f"""
<p>Passport Holders(Having at least one Passport stamp): {holders_count}</p>
<p>Non Passport Holders: {non_hodler_count}</p>
"""
st.markdown(holders_str, unsafe_allow_html=True)


stamp_count_fig = px.histogram(holders, x="valid_stamps_count", title="Number of stamps among Passport holders")
st.plotly_chart(stamp_count_fig)

holders['date'] = pd.to_datetime(holders['issuance_date']).dt.date

issuarance_by_date =  holders.groupby('date').count()['address']
issuarance_fig = px.bar(issuarance_by_date, y='address', title='Bar chart of stamp issuarance date')
st.plotly_chart(issuarance_fig)

st.write("""
We can observe that many contributors of GR15 issued stamps during GR15 period(September 07-22).
""")

st.subheader("3. Analysis through stamp_holders_ratio")

st.markdown("""
We defined stamp_holders_ratio as follows.

*Stamp Holders Ratio = Contributors of holding stamps / Total Contributors*

Stamp Holders Ratio can have a range 0.0~1.0. 
The more contributors by stamp holders, the higher this ratio be.
""")

grants_stamps = get_grants_stamps()
top = get_top50()
fig = go.Figure()
fig.add_trace(go.Histogram(x=grants_stamps['holders_ratio'], name='all'))
fig.add_trace(go.Histogram(x=top['holders_ratio'], name='top50_grants'))
fig.update_layout(barmode='overlay', title='Histgram of Stamp Holders Ratio')
fig.update_traces(opacity=0.75)
st.plotly_chart(fig)
# ratio_fig = px.histogram(grants_stamps, x="holders_ratio", title="Histgram of Holders Ratio")
# st.plotly_chart(ratio_fig)

st.markdown("""
We split grants into three categories as follows.
1. High: Stamp Holders Ratio > 0.75
2. Normal: Stamp Holders Ratio >= 0.25, <= 0.75
3. Low: Stamp Holders Ratio < 0.25

We assume that some of them in high and low ratio group are suspicious actor/attacker and there are some statistical difference from normal group.
""")

grants_by_ratio = get_grants_by_ratio()
high = grants_by_ratio[grants_by_ratio['holders_ratio_category'] == 'high']
low = grants_by_ratio[grants_by_ratio['holders_ratio_category'] == 'low']
normal = grants_by_ratio[grants_by_ratio['holders_ratio_category'] == 'normal']
grants_by_ratio_fig = px.histogram(grants_by_ratio, x="amount_per_contributor", color="holders_ratio_category",
                   marginal="box", # or violin, rug
                   )
st.plotly_chart(grants_by_ratio_fig)
# grants_by_ratio_box = px.box(grants_by_ratio, x="holders_ratio_category", y="amount_per_contributor")
# st.plotly_chart(grants_by_ratio_box)

st.markdown("""
We observe that average donation amount per contributors is statistically significant difference between low_ratio, high_ratio and normal group.
Average donation amount is lower than normal group.
""")

st.markdown("#### T-Test result")
result_amount_high = mannwhitneyu(high['amount_per_contributor'], normal['amount_per_contributor'])
result_amount_low = mannwhitneyu(low['amount_per_contributor'], normal['amount_per_contributor'])
result_amount_high
result_amount_low
# result_high = ttest_ind(high['amount_per_contributor'], normal['amount_per_contributor'], equal_var=False)
# result_low = ttest_ind(low['amount_per_contributor'], normal['amount_per_contributor'], equal_var=False)


# holders_str = f"""
# <p>P Value of high_ratio vs normal group: {result_high.pvalue}</p>
# <p>P Value of low_ratio vs normal group:  {result_low.pvalue}</p>
# """
# st.markdown(holders_str, unsafe_allow_html=True)

contributors_hist = px.histogram(grants_by_ratio, x="contributor_count_in_round", color="holders_ratio_category",
                   marginal="box", # or violin, rug
                   )
st.plotly_chart(contributors_hist)

# contributors_box = px.box(grants_by_ratio, x="holders_ratio_category", y="contributor_count_in_round")
# st.plotly_chart(contributors_box)

st.markdown("#### T-Test result")
result_contributor_high = mannwhitneyu(high['contributor_count_in_round'], normal['contributor_count_in_round'])
result_contributor_low = mannwhitneyu(low['contributor_count_in_round'], normal['contributor_count_in_round'])
# result_contributor_high = ttest_ind(high['contributor_count_in_round'], normal['contributor_count_in_round'], equal_var=True)
# result_contributo_low = ttest_ind(low['contributor_count_in_round'], normal['contributor_count_in_round'], equal_var=True)
result_contributor_high
result_contributor_low

# holders_str = f"""
# <p>P Value of high_ratio vs normal group: {result_contributor_high}</p>
# <p>P Value of low_ratio vs normal group:  {result_contributo_low.pvalue}</p>
# """
# st.markdown(holders_str, unsafe_allow_html=True)

fig = px.scatter(grants_by_ratio,
    x='contributor_count_in_round', y='amount_per_contributor',
    color="holders_ratio_category"
    ,hover_name='title')
st.plotly_chart(fig)

st.markdown("""
We observe that number of contributors in low_ratio group is much higher than other groups.

We can understand this behaivoir, attackers in low_ratio group put more effort on creating puppet account than collecting stamps.
""")

st.subheader("4. Summary & Proposals")

st.markdown("""
We conclude the following two groups of grant are suspicious as sybil attackers.
1. low stamp holders ratio + small average amount donations + many contributors
2. high stamp holders ratio + small average amount donations

We are not saying all of grants in above groups are attackers, but we believe some attackers got mixed in among above groups.


""")