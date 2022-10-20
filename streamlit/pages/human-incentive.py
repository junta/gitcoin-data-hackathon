
import streamlit as st
#import seaborn as sns
import pandas as pd
import plotly.express as px

st.markdown("# Hack Human Incentive")
st.sidebar.markdown("# hack Human Incentive")

st.write("""
In this bounty, We analyzied score of Github repository of each grant provided. 
And propose a method to make screening process better with repository score at last.
""")

st.markdown("""
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

top_scored = pd.read_csv('./streamlit/data/top200.csv')
st.table(top_scored.head(10))

st.write("We can see many famous projects in this list and it's reliable socre.")


st.subheader("2. Overview of critical score of grantee of GR15")

st.write("""
We have gathered this score for all applicable projects of Gitcoin round 15.
Of course, not all projects provided their github_repo_url.
""")

grants = pd.read_csv('../grants.csv') 
no_github = grants[grants['github_project_url'].isna()].count()

st.markdown("""
Among 1502 approved grants in GR15, **937** projects provided their Github URL, and **565** projects did not.


""")

valid_repo = pd.read_csv('../github/valid_repos.csv')
repository_score = pd.read_csv('../github/repository_score.csv') 
d = {'name': ['repo_page', 'profile_page', '404_not_found'], 'count': [0, 0, 0]}
repo_count = pd.DataFrame(d)

repo_count.iloc[0, 1] = valid_repo.count()['grant_id']
repo_count.iloc[1, 1] = repository_score[(repository_score['status_code'] == 200) & (repository_score['returncode'] == 1)].count()['grant_id']
repo_count.iloc[2, 1] = repository_score[repository_score['status_code'] == 404].count()['grant_id']

fig = px.pie(repo_count, values='count', names='name')
st.plotly_chart(fig)

