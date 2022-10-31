
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
In this analysis, We focused on one type of Sybil, attacker(not farmer). 
We conducted exploratory data analysis combined with Gitcoin Passport data to identify potential Sybils and figure out their behavior.
We categorized each grant into three categories by Stamp Holders Ratio, and 
observed differences among them.
""")

st.markdown("""
    #### table of contents:
    1. Introduction and Hypothesis
    2. Overview of Gitcoin Passport data
    3. Analysis through Stamp Holders Ratio
    4. Summary & Proposals
""")

st.subheader("1. Introduction and Hypothesis")
st.markdown("""
Attackers cheat on Quadratic Funding and donate to their own projects by themselves to maximize QF impact.

We assume their characteristics and behavior are as follows.
- Have many small amount contributions, and average contribution amount is lower than others.
- Have too many contributors compared to projects that received a similar amount contributions. (Because they created lots of sock puppet accounts)
- May collect passport stamps if they are highly motivated(to get Trust Bonus and maximize impact), but some don't do because it is time-consuming work.
Those are valid reasoning, given how the Quadratic Funding system works.
""")

st.text("")

st.subheader("2. Overview of Gitcoin Passport data")
st.markdown("""
We gathered Gitcoin Passport data of all contributors in Round 15 by [Gitcoin Passport SDK: Reader](https://github.com/gitcoinco/passport-sdk/tree/main/packages/reader).

And filtered their stamps to valid stamps as issuance date is before 2022-09-23(the last day of GR15) and not expired yet.
Then aggregated stamps count and merged them into grants dataset.

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


stamp_count_fig = px.histogram(holders, x="valid_stamps_count", title="Number of stamps they collected among Passport holders")
st.plotly_chart(stamp_count_fig)

holders['date'] = pd.to_datetime(holders['issuance_date']).dt.date

issuarance_by_date =  holders.groupby('date').count()['address']
issuarance_fig = px.bar(issuarance_by_date, y='address', title='Bar chart of stamp issuarance date')
st.plotly_chart(issuarance_fig)

st.write("""
Many contributors of GR15 issued stamps during GR15 period(September 07-22).
""")

st.text("")

st.subheader("3. Analysis through Stamp Holders Ratio")

st.markdown("""
We would like to introduce Stamp Holders Ratio and defined them as follows.

For each grant,

*Stamp Holders Ratio = Contributors of holding stamps / Total Contributors*

Stamp Holders Ratio can have a range of 0.0~1.0. 
The more stamp holder contributors, the higher this ratio is.
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

# st.dataframe(grants_stamps.describe())

st.write("""
The above graph also shows overlaid histogram of the top 50 projects(grants) with the highest amount of contributions received in GR15.
Their Stamp Holders Ratio ranges from 0.33 to 0.68 and has a normal distribution.

Mean value of holders_ratio among all grants is 0.53. This means for each grant, around half of their contributors are non-stamp holders, and the other half are stamp holders on average.
""")

st.markdown("""
Then, We split grants into three categories by Stamp Holders Ratio as follows.
| Category   | Description                                                                                                                               |
|------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| High ratio | Top 50 projects with the highest stamp holder ratio                                                                                       |
| Low ratio  | Bottom 50 projects with the lowest stamp holder ratios                                                                                    |
| Normal     | Others. (Projects not included in either of top50 or high/low ratio groups fall into this group. random sampled 50, when showing charts.) |

""")
st.text("")

st.write("We also filtered out grants which contribution count is less than 10 because number of samples is too small to calculate the stamp holders ratio.")

grants_by_ratio = get_grants_by_ratio()
high = grants_by_ratio[grants_by_ratio['holders_ratio_category'] == 'high']
low = grants_by_ratio[grants_by_ratio['holders_ratio_category'] == 'low']
normal = grants_by_ratio[grants_by_ratio['holders_ratio_category'] == 'normal']

st.markdown("#### List of Grants by category")
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
We assume that some of the grants in high and low ratio groups are suspicious as attackers, because they are likely manipulated artificially if the ratio is too high or low.
And there would be some statistical difference from the normal group.
""")

grants_by_ratio_fig = px.histogram(grants_by_ratio, x="amount_per_contributor", color="holders_ratio_category",
                   marginal="box", # or violin, rug
                   title='Histgram of Average contribution amount in USD per contributor'
                   )
st.plotly_chart(grants_by_ratio_fig)
# grants_by_ratio_box = px.box(grants_by_ratio, x="holders_ratio_category", y="amount_per_contributor")
# st.plotly_chart(grants_by_ratio_box)

st.markdown("**Mann-Whitney U Test result:**")
result_amount_high = mannwhitneyu(high['amount_per_contributor'], normal['amount_per_contributor'])
result_amount_low = mannwhitneyu(low['amount_per_contributor'], normal['amount_per_contributor'])
holders_str = f"""
<p>P Value of high_ratio vs normal group: {result_amount_high.pvalue}</p>
<p>P Value of low_ratio vs normal group:  {result_amount_low.pvalue}</p>
"""
st.markdown(holders_str, unsafe_allow_html=True)

st.markdown("""
We observe that average contribution amount per contributor is statistically significant different between low_ratio and normal group.

Median value in high_ratio is a bit lower than normal group, but no statistically significant difference between them.
""")

# result_high = ttest_ind(high['amount_per_contributor'], normal['amount_per_contributor'], equal_var=False)
# result_low = ttest_ind(low['amount_per_contributor'], normal['amount_per_contributor'], equal_var=False)



contributors_hist = px.histogram(grants_by_ratio, x="contributor_count_in_round", color="holders_ratio_category",
                   marginal="box", # or violin, rug
                   title='Histgram of number of contributors'
                   )
st.plotly_chart(contributors_hist)

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

st.write("""
It is clear that the distribution of low ratio group is extraordinary, their number of contributors is much higher than other groups.

We can understand this behavior; attackers in low_ratio group put more effort into creating puppet accounts than collecting stamps.
On the other hand, the distribution of high_ratio group has a similar form to normal group.
""")


st.text("")

st.write("""
Assuming there are no Sybil attackers, distribution of the above two charts should be the same for all three groups.
""")

# contributors_box = px.box(grants_by_ratio, x="holders_ratio_category", y="contributor_count_in_round")
# st.plotly_chart(contributors_box)


fig = px.scatter(grants_by_ratio,
    x='contributor_count_in_round', y='amount_per_contributor',
    color="holders_ratio_category"
    ,hover_name='title'
    ,hover_data=['holders_ratio']
    ,title='Scatter plots')
st.plotly_chart(fig)

st.write("""
In the scatter plot, it is more evident that some of the grants in low ratio group(Green) have too many contributors and too small an amount per contributor compared to the other two groups.
""")

st.markdown("""
    #### Suspicious projects(as Sybil attacker)
    (contributor_count_in_round > 500) and (amount_per_contributor < 3.0) and in low_ratio group
""")
suspicious = grants_by_ratio[(grants_by_ratio['contributor_count_in_round'] > 500) & (grants_by_ratio['amount_per_contributor'] < 3) & (grants_by_ratio['holders_ratio_category'] == 'low')]
st.dataframe(suspicious)

st.text("")

st.subheader("4. Summary & Proposals")

st.markdown("""
In conclusion, they are likely to be Sybil attackers if they have low stamp holders ratio + too small average amount of contributions + too many contributors.

We assumed some of the grants in high_ratio group might also be suspicious, but we could not find statistical differences between them and normal group.

We believe Gitcoin team can introduce this method as one of the Sybil detection legos.
""")