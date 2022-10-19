import subprocess
import pandas as pd

grants = pd.read_json('./GR15_public_hackathon/gr15_grants.json')
grants = grants.transpose()
grants = grants[grants['grant_id'] != 12]
grants = grants.dropna(subset=['github_project_url'])
grants = grants.query('github_project_url.str.startswith("https://github.com")')

grants = grants.reset_index(drop=True)
grants_score = grants[['grant_id','github_project_url']]
grants_score['returncode'] = None
grants_score['stdout'] = None

#print(grants_score)

for index, row in grants_score.iterrows():
    print(index)
    # score = subprocess.run(['criticality_score', '--repo', 'https://github.com/SambaGod/IkhalaPlatform'], capture_output=True, text=True)
    score = subprocess.run(['criticality_score', '--repo', row['github_project_url']], capture_output=True, text=True)
    print(score)
    grants_score.iloc[index, 2] = score.returncode
    grants_score.iloc[index, 3] = score.stdout
    
    grants_score.to_csv('repository_score.csv', index=False)    