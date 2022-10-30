
import streamlit as st
#import seaborn as sns
import pandas as pd
import plotly.express as px

@st.cache
def get_top_repos():
    return pd.read_csv('./github/top200.csv')

@st.cache
def get_valid_repo():
    return pd.read_csv('./github/valid_repos.csv')

@st.cache
def get_grants():
    return pd.read_csv('./public_data/grants.csv')

@st.cache
def get_valid_grants():
    valid_grants = pd.merge(get_valid_repo(), get_grants(), on='grant_id')
    valid_grants.rename(columns={'github_project_url_x': 'github_project_url'}, inplace = True)
    return valid_grants

@st.cache
def get_repo_count_by_category():
    valid_repo = get_valid_repo()
    repository_score = pd.read_csv('./github/repository_score.csv') 
    grants = get_grants()
    grants = grants.dropna(subset=['github_project_url'])

    d = {'isValid': ['valid', 'valid', 'invalid', 'invalid'], 
    'category': ['repo_url', 'profile_url', '404_not_found', 'not_github_url'], 
    'example': ['https://github.com/ethers-io/ethers.js/', 'https://github.com/Sol-DAO', 'https://github.com/SambaGod/IkhalaPlatform', 'https://gitcoin.co/glennpoppe'] ,
    'count': [0, 0, 0, 0]}
    repo_count = pd.DataFrame(d)

    repo_count.iloc[0, 3] = valid_repo.count()['grant_id']
    repo_count.iloc[1, 3] = repository_score[(repository_score['status_code'] == 200) & (repository_score['returncode'] == 1)].count()['grant_id']
    repo_count.iloc[2, 3] = repository_score[repository_score['status_code'] == 404].count()['grant_id']
    repo_count.iloc[3, 3] = grants[~grants['github_project_url'].str.contains('github.com')].count()['grant_id']
    return repo_count

# -------Page

st.markdown("# Hack Human Incentive")
st.sidebar.markdown("# hack Human Incentive")

st.write("""
We analyzed each grant's Github repository score in this bounty. 
And propose a method to make reviewing process of grant applications better with the repository score at last.
""")

st.markdown("""
    #### table of contents:
    1. Introduction of Github Critical Score
    2. Data Overview of GR15 grant's Github Critical Score
    3. Correlation between Github score and other grant's data
    4. Summary & Proposals
""")

st.subheader("1. Introduction of Github Critical Score")

st.markdown("""
The goal of this bounty is to make observations and propose improvements about how to grade grants for their eligibility.

[Open Source Project Criticality Score](https://github.com/ossf/criticality_score), 
built and maintained by Securing Critical Projects WG of [OpenSSF](https://openssf.org/), 
generates a criticality score for any open-source projects.

The criticality_score takes into consideration [a variety of parameters](https://github.com/ossf/criticality_score#criticality-score), 
for example, commit_frequency, contributor_count, etc..., and their repository has over 1K stars.

Here are tge top 10 highest-scored repositories across all languages.
""")

st.dataframe(get_top_repos().head(10))

st.write("We can see many famous projects in the list, and their reliable scores.")

st.text("")

st.subheader("2. Data Overview of GR15 grant's Github Critical Score")

st.write("""
We have gathered the score for all applicable grants of Gitcoin round 15. We did this process on Oct 19th, so the scores we gathered could be different from scores during GR15.

Of course, this method can apply to only development projects they have Github repository, and not all projects provided their github_repo_url.
""")

#no_github = grants[grants['github_project_url'].isna()].count()

st.markdown("""
Among 1502 approved grants in GR15, **928** projects provided their Github URL, and **574** projects did not.
""")

st.text("")

st.markdown("""
We can categorize those 928 URLs into the four following categories.
- Repository URL: Direct link to a certain repository
- Profile URL: Link to their organization or profile account
- 404 Not Found: did not provide a valid URL or delete the repository after GR15.
- Not Github URL: did not provide Github URL.(their own website URL, Gitcoin profile URL, etc...)
""")


st.table(get_repo_count_by_category())

fig = px.pie(get_repo_count_by_category(), values='count', names='category')
st.plotly_chart(fig)

st.markdown("**About 9.5% of approved projects(87 projects) provided invalid URL(404_not_found + not_github_url) as Github URL.**")

st.write("""
Although submitting Github profile URL(profile_url) is valid, We excluded them from our scoring analysis because
we have to specify one main repository to generate the score..
""")

st.text("")

valid_grants = get_valid_grants()

st.write("""Top 5 scored projects:""")
st.dataframe(valid_grants.sort_values('score', ascending=False).head(5)[['grant_id', 'title', 'score', 'github_project_url']])
#st.table(get_valid_grants().head())

st.write("""On the other hand, the lowest 5 scored projects:""")
st.dataframe(valid_grants.sort_values('score').head(5)[['grant_id', 'title', 'score', 'github_project_url']])

st.write("""A typical example of lowest scored project:""")
st.markdown("[Malicious Contract Detector](https://github.com/0xidase/Malicious-Contract-Detector)")
st.image('./streamlit/images/Malicious-Contract-Detector.png')
st.write("""This repository has nothing but just README or License files!""")


fig = px.histogram(valid_grants, x="score", title="Histgram of grant's Github Score")
st.plotly_chart(fig)

st.dataframe(valid_grants.describe()['score'])

st.markdown("You can find scores for all applicable projects [here](https://github.com/junta/gitcoin-data-hackathon/blob/main/github/valid_repos.csv).")

st.text("")

st.subheader("3. Correlation between Github score and other grant's data")

fig = px.scatter(valid_grants, x='score', y='amount_received', hover_name='title', trendline='ols', trendline_color_override='darkblue', labels={"amount_received": "Total Received USD Amount", "score": "Github Score"}, title="Total Received donation Amount in USD")
st.plotly_chart(fig)

fig = px.scatter(valid_grants, x='score', y='amount_received_in_round', hover_name='title', trendline='ols', trendline_color_override='darkblue',  labels={"amount_received": "GR15 Received USD Amount", "score": "Github Score"}, title="GR15 Received donation Amount in USD")
st.plotly_chart(fig)

st.write("Correlation coefficient between Github score and other variables")
for_corr = valid_grants[['score', 'amount_received', 'amount_received_in_round','contribution_count', 'contributor_count']]
st.table(for_corr.corr())

st.write("""
We can observe some correlation between score and amount_received, contribution_count, contributor_count. 

But surprisingly little correlation between score and amount_received_in_round.
This means that top scored project has more donation amount/contributions/contributors in all past period, but not so much in round 15.
""")

st.text("")

st.write("""
In addition, this score may also be helpful to find undervalued projects(High-scored but less donation amount received). 
""")

st.markdown("""
    #### Projects of score > 0.5 and amount_received < 100K
""")

undervalued = valid_grants[(valid_grants['score'] > 0.5) & (valid_grants['amount_received'] < 100000)].sort_values('score', ascending=False)[['grant_id', 'title', 'score', 'amount_received', 'github_project_url']]
st.dataframe(undervalued)

st.text("")

# col1, col2 = st.columns(2)

# with col1:
#     fig = px.histogram(get_valid_repo(), x="score", title="Histgram of grant's Github Score")
#     st.plotly_chart(fig)
# with col2:
#     st.dataframe(get_valid_repo().describe()['score'])

st.subheader("4. Summary & Proposals")

st.markdown("""
    1. In GR15, 87 projects provided invalid Github URL. Those projects might submit wrong URL, but also might not be eligible for Gitcoin grants round.
    **Proposal:** Introducing checking provided URL is valid or not and filtering out invalid ones or show a warning alert.
    This could be implemented in grant application page of Gitcoin application or reviewing process.  


    2. Low-scored projects(ex. less than 0.1 score) may be fake projects or may not be eligible for Gitcoin grants round.
    **Proposal:** Utilizing the scoring tool in the review process. 
    For example, run the scoring tool automatically and add label them "Suspicious" If score < 0.1.
    Then reviewer checks them one by one manually with their other materials(Twitter account, project URL, etc...).

    3. High-scored projects have received more contributions in the long run historically. (r = 0.4~0.49)
""")