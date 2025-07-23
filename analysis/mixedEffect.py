import statsmodels.formula.api as smf
from ast import mod
import json
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data
with open('parsed_participants.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

valence_partner = []
valence_self = []
arousal_partner = []
arousal_self = []
confidence_partner = []
confidence_self = []
data_id = 1

def parse_condition(cond):
    robot = 1 if 'B+' in cond else 0
    touch = 1 if 'T+' in cond else 0
    return robot, touch

for user in data:
    user_id = user['id']
    for cond, cond_data in user['conditions'].items():
        robot, touch = parse_condition(cond)
        for t_idx, timepoint in enumerate(cond_data['timePoints']):
            # Partner
            valence_partner.append({
                'data_id': data_id,
                'user_id': user_id,
                'robot': robot,
                'touch': touch,
                'emotion': t_idx + 1,
                'value': timepoint['partner']['valence']
            })
            arousal_partner.append({
                'data_id': data_id,
                'user_id': user_id,
                'robot': robot,
                'touch': touch,
                'emotion': t_idx + 1,
                'value': timepoint['partner']['arousal']
            })
            confidence_partner.append({
                'data_id': data_id,
                'user_id': user_id,
                'robot': robot,
                'touch': touch,
                'emotion': t_idx + 1,
                'value': timepoint['partner']['confidence']
            })
            # Self
            valence_self.append({
                'data_id': data_id,
                'user_id': user_id,
                'robot': robot,
                'touch': touch,
                'emotion': t_idx + 1,
                'value': timepoint['self']['valence']
            })
            arousal_self.append({
                'data_id': data_id,
                'user_id': user_id,
                'robot': robot,
                'touch': touch,
                'emotion': t_idx + 1,
                'value': timepoint['self']['arousal']
            })
            confidence_self.append({
                'data_id': data_id,
                'user_id': user_id,
                'robot': robot,
                'touch': touch,
                'emotion': t_idx + 1,
                'value': timepoint['self']['confidence']
            })
            data_id += 1

# Convert to DataFrames
valence_partner_df = pd.DataFrame(valence_partner)
valence_self_df = pd.DataFrame(valence_self)
arousal_partner_df = pd.DataFrame(arousal_partner)
arousal_self_df = pd.DataFrame(arousal_self)
confidence_partner_df = pd.DataFrame(confidence_partner)
confidence_self_df = pd.DataFrame(confidence_self)

# Mixed model with user as random effect
mixed_model = smf.mixedlm("value ~ robot * touch * emotion", 
                          valence_partner_df, 
                          groups=valence_partner_df["user_id"]).fit()
print(mixed_model.summary())

#arousal mixed model
mixed_model = smf.mixedlm("value ~ robot * touch * emotion", 
                        arousal_partner_df, 
                        groups=arousal_partner_df["user_id"]).fit()
print(mixed_model.summary())

#confidence mixed model
mixed_model = smf.mixedlm("value ~ robot * touch * emotion", 
                        confidence_partner_df, 
                        groups=confidence_partner_df["user_id"]).fit()
print(mixed_model.summary())

#valence self mixed model
mixed_model = smf.mixedlm("value ~ robot * touch * emotion", 
                        valence_self_df, 
                        groups=valence_self_df["user_id"]).fit()   
print(mixed_model.summary())

#arousal self mixed model
mixed_model = smf.mixedlm("value ~ robot * touch * emotion", 
                        arousal_self_df, 
                        groups=arousal_self_df["user_id"]).fit()
print(mixed_model.summary())

#confidence self mixed model
mixed_model = smf.mixedlm("value ~ robot * touch * emotion", 
                        confidence_self_df, 
                        groups=confidence_self_df["user_id"]).fit()
print(mixed_model.summary())


import numpy as np
import matplotlib.pyplot as plt

emotions = np.array([1, 2, 3, 4, 5])
robot_0 = 4.725 + 0.050 * emotions  # baseline
robot_1 = 4.725 + 0.538 + (0.050 - 0.175) * emotions  # with robot

plt.figure(figsize=(8, 6))
plt.plot(emotions, robot_0, 'o-', label='No Robot', linewidth=2)
plt.plot(emotions, robot_1, 's-', label='Robot', linewidth=2)
plt.xlabel('Emotion Level')
plt.ylabel('Arousal Rating')
plt.title('Robot × Emotion Interaction for Partner Arousal')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xticks(emotions)
plt.show()