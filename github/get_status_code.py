import subprocess
import pandas as pd
import requests
import time

scores = pd.read_csv('repository_score.csv')

scores['status_code'] = None

print(scores.head())

for index, row in scores.iterrows():
    print(index)
    response = requests.get(row['github_project_url'])
    
    scores.iloc[index, 4] = response.status_code
    
    scores.to_csv('repository_score.csv', index=False)

    time.sleep(0.2)