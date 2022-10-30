
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
    #### table of contents:
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

And filtered their stamps to valid stamps as issuanceDate is before 2022-09-23(the last day of GR15) and not expired yet, then aggregated stamps count and merged into grants dataset.

You can find [grants_stamps.csv data here](https://github.com/junta/gitcoin-data-hackathon/blob/main/analytics_data/grants_stamps.csv).
""")

passport = get_passports()

non_hodler_count = passport[passport['valid_stamps_count'] == 0.0].count()['address']
# 36,536
holders_count = passport[passport['valid_stamps_count'] != 0.0].count()['address']
# 19,049 
holders = passport[passport['valid_stamps_count'] != 0.0]

st.markdown("""
|                                                      | count  |
|------------------------------------------------------|--------|
| Passport Holders(Having at least one Passport stamp) | 19,049 |
| Non Passport Holders                                 | 36,536 |
""")


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
We would like to introduce Stamp Holders Ratio and defined them as follows.

For each grant,

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

st.write("""
Showing overlaid histogram of top 50 projects(grants) with the highest amount of donations received in GR15.
Their Stamp Holders Ratio is range from 0.33 to 0.68 and has normal distribution.
""")

st.markdown("""
Then, We split grants into three groups by Stamp Holders Ratio as follows.
| Category   | Description                                                                                                                               |
|------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| High ratio | Top 50 projects with the highest stamp holder ratio                                                                                       |
| Low ratio  | Bottom 50 projects with the lowest stamp holder ratios                                                                                    |
| Normal     | Rest of them. (Projects not included in either of top50 or high/low ratio groups fall into this group. random sampled 50, when show charts.) |

""")
st.text("")

st.write("We also filtered out grants of which contribution count is less than 10 because number of samples is too little to calculate stamp holders ratio.")

grants_by_ratio = get_grants_by_ratio()
high = grants_by_ratio[grants_by_ratio['holders_ratio_category'] == 'high']
low = grants_by_ratio[grants_by_ratio['holders_ratio_category'] == 'low']
normal = grants_by_ratio[grants_by_ratio['holders_ratio_category'] == 'normal']

st.markdown("#### List of Grants in each group")
tab1, tab2, tab3, tab4 = st.tabs(["Top", "Normal", "High Ratio", "Low Ratio"])
with tab1:
    st.dataframe(top)
with tab2:
    st.dataframe(normal)
with tab3:
    st.dataframe(high)
with tab4:
    st.dataframe(low)

st.write("""
We assume that some of grants in high and low ratio group are suspicious actor/attacker and there would be some statistical difference from normal group.
""")

grants_by_ratio_fig = px.histogram(grants_by_ratio, x="amount_per_contributor", color="holders_ratio_category",
                   marginal="box", # or violin, rug
                   title='Histgram of Average donation amount in USD per contributor'
                   )
st.plotly_chart(grants_by_ratio_fig)
# grants_by_ratio_box = px.box(grants_by_ratio, x="holders_ratio_category", y="amount_per_contributor")
# st.plotly_chart(grants_by_ratio_box)

st.markdown("""
We observe that average donation amount per contributors is statistically significant difference between low_ratio and normal group.

Median value in high_ratio is a bit lower than normal group, but no  statistically significant difference between them.
""")

st.markdown("**Mann-Whitney U Test result:**")
result_amount_high = mannwhitneyu(high['amount_per_contributor'], normal['amount_per_contributor'])
result_amount_low = mannwhitneyu(low['amount_per_contributor'], normal['amount_per_contributor'])

# result_high = ttest_ind(high['amount_per_contributor'], normal['amount_per_contributor'], equal_var=False)
# result_low = ttest_ind(low['amount_per_contributor'], normal['amount_per_contributor'], equal_var=False)


holders_str = f"""
<p>P Value of high_ratio vs normal group: {result_amount_high.pvalue}</p>
<p>P Value of low_ratio vs normal group:  {result_amount_low.pvalue}</p>
"""
st.markdown(holders_str, unsafe_allow_html=True)

contributors_hist = px.histogram(grants_by_ratio, x="contributor_count_in_round", color="holders_ratio_category",
                   marginal="box", # or violin, rug
                   title='Histgram of number of contributors in GR15'
                   )
st.plotly_chart(contributors_hist)

st.write("""
It is clear that distribution of low ratio group is extraordinary, thier number of contributors is much higher than other groups.

We can understand this behaivoir, attackers in low_ratio group put more effort on creating puppet account than collecting stamps.
On the other hand, distribution of high_ratio group has a similar form to normal group.
""")

st.markdown("**Mann-Whitney U Test result:**")
result_contributor_high = mannwhitneyu(high['contributor_count_in_round'], normal['contributor_count_in_round'])
result_contributor_low = mannwhitneyu(low['contributor_count_in_round'], normal['contributor_count_in_round'])
# result_contributor_high = ttest_ind(high['contributor_count_in_round'], normal['contributor_count_in_round'], equal_var=True)
# result_contributo_low = ttest_ind(low['contributor_count_in_round'], normal['contributor_count_in_round'], equal_var=True)

holders_str = f"""
<p>P Value of high_ratio vs normal group: {result_contributor_high.pvalue}</p>
<p>P Value of low_ratio vs normal group:  {result_contributor_low.pvalue}</p>
"""
st.markdown(holders_str, unsafe_allow_html=True)

st.text("")

st.write("""
Assuming there are no sybil attackers, distribution of above two charts should be the same for all of the three groups.
""")

# contributors_box = px.box(grants_by_ratio, x="holders_ratio_category", y="contributor_count_in_round")
# st.plotly_chart(contributors_box)


fig = px.scatter(grants_by_ratio,
    x='contributor_count_in_round', y='amount_per_contributor',
    color="holders_ratio_category"
    ,hover_name='title'
    ,title='Scatter plots')
st.plotly_chart(fig)

st.write("""
In the scatter plot, it is more evident that some of the grants in low ratio group(Green) have too many contributors and too small amount per contributor, compared to the other two groups.
""")


st.subheader("4. Summary & Proposals")

st.markdown("""
In conclusion, they are likely to be sybil attackers if they have low stamp holders ratio + too small average amount donations + too many contributors.

some of grants having high stamp holders ratio may also suspicious, but we could not find statistical difference between them and normal group.

We belive Gitcoin team can introduce this method as one of the sybil detection legos.
""")