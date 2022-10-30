
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
def get_merged_repo_data():
    return pd.merge(get_valid_repo(), get_grants(), on='grant_id')

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
In this bounty, We analyzied score of Github repository of each grant provided. 
And propose a method to make screening process better with repository score at last.
""")

st.markdown("""
    #### table of contents:
    1. Introduction of Github critical score
    2. Overview of critical score of grantee of GR15
    3. Correlation between critical score and other variables
    4. Summary & Proposals
""")

st.subheader("1. Introduction of Github critical score")

st.markdown("""
The goal of this bounty is that providing a method to help reviewing process of Gitcoin grant.
Github repository URL is provided in application process, and 
We believe scoring Github repository is one possible nice method to filter grants for development projects.

[Open Source Project Criticality Score](https://github.com/ossf/criticality_score), 
built and maitained by Securing Critical Projects WG of [OpenSSF](https://openssf.org/), 
generates a criticality score for every open source project.

The criticality_score takes into consideration [a variety of parameters](https://github.com/ossf/criticality_score#criticality-score), 
for example commit_frequency, contributor_count, etc..., and their repository has over 1K stars.

Here is top 10 highest scored repositories across all languages.
""")

st.table(get_top_repos().head(10))

st.write("We can see many famous projects in this list and it's reliable socre.")


st.subheader("2. Overview of critical score of grantee of GR15")

st.write("""
We have gathered this score for all applicable projects of Gitcoin round 15.
We did this process at Oct 19th, so scores we gathered could be different from scores during GR15.
Of course, not all projects provided their github_repo_url.
""")

#no_github = grants[grants['github_project_url'].isna()].count()

st.markdown("""
Among 1502 approved grants in GR15, **928** projects provided their Github URL, and **574** projects did not.
""")

st.text("")

st.markdown("""
We can categorize those 928 URL into the four following category.
- Repository URL: Direct link to a certain repository
- Profile URL: Link to organization or profile account URL
- 404 Not Found: did not provide valid URL or deleted the repository after GR15.
- Not Github URL: provided not Github URL.(their own website URL, profile URL of Gitcoin, etc...)
""")


st.table(get_repo_count_by_category())

fig = px.pie(get_repo_count_by_category(), values='count', names='category')
st.plotly_chart(fig)

st.markdown("**Key takeaway here is about 9.5% of approved projects provided invalid URL as Github URL**")

st.write("""Top 10 scored projects""")
st.table(get_merged_repo_data().sort_values('score', ascending=False).head(10)[['grant_id', 'title', 'score', 'github_project_url_x']])
#st.table(get_merged_repo_data().head())

st.write("""On the other hands, lowest scored projects""")
st.table(get_merged_repo_data().sort_values('score').head(5)[['grant_id', 'title', 'score', 'github_project_url_x']])

st.write("""A typical example of lowest score project""")
st.image('./streamlit/images/Malicious-Contract-Detector.png')
st.write("""This repository nothing but just README or License files!""")


st.write("""Histgram of repositories by score""")
fig = px.histogram(get_valid_repo(), x="score")
st.plotly_chart(fig)

st.write("""
Although subitting Github profile URL is valid, We excluded them from our scoring analysis because
we have to speficy main one repository to generate score.
""")


st.subheader("3. Correlation between critical score and other variables")

fig = px.scatter(get_merged_repo_data(), x='score', y='amount_received', hover_name='title', trendline='ols', trendline_color_override='darkblue')
st.plotly_chart(fig)

fig = px.scatter(get_merged_repo_data(), x='score', y='amount_received_in_round', hover_name='title', trendline='ols', trendline_color_override='darkblue')
st.plotly_chart(fig)

fig = px.scatter(get_merged_repo_data(), x='score', y='contribution_count', hover_name='title')
st.plotly_chart(fig)

fig = px.scatter(get_merged_repo_data(), x='score', y='contributor_count', hover_name='title')
st.plotly_chart(fig)

st.write("Correlation between score and other variables")
for_corr = get_merged_repo_data()[['score', 'amount_received', 'amount_received_in_round','contribution_count', 'contributor_count']]
st.table(for_corr.corr())

st.write("""
We can observe some correlation between score and amount_received, contribution_count, contributor_count. 
But little correlation between score and amount_received_in_round.
This means that top scored project has more donation amount/contribution/contributor all-time, but not so much in round 15 with some reasons.
""")

# col1, col2 = st.columns(2)

# with col1:
#     col1.px.scatter(get_merged_repo_data(), x='score', y='amount_received')
#     col1.st.plotly_chart(fig)
# with col2:
#     fig = px.scatter(get_merged_repo_data(), x='score', y='amount_received_in_round')
#     st.plotly_chart(fig)

st.subheader("4. Summary & Proposals")

st.markdown("""
    1. In round 15, 87 projects provided invalid Github URL. Those projects but also may not eligible for grant.
    **Proposal:** Introducing checking provided URL is valid or not and filtering out invalid one or show warning alert automatically.
    This could be inplemented in grant application page of Gitcoin frontend app or reviewing process.

    2. Low scored projects(ex. less than 0.1 score) may be fake projects or may not eligible for grant.
    **Proposal:** Utilizing the scoring tool in review process. 
    For example, run the tool automatically and add label them "Be carefule" If score < 0.1.
    Then reviewer check each of them manually.

    2. High scored projects have received more contributions in the long run. (r = 0.4~0.5)
    **Proposal:** Measuring score with a certain inverval(once per quarter, for example) to check progress of each grants.
""")