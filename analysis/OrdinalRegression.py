from statsmodels.miscmodels.ordinal_model import OrderedModel


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


# Ordinal logistic regression
mod_ord = OrderedModel(valence_partner_df['value'], 
                      valence_partner_df[['robot', 'touch', 'emotion']], 
                      distr='logit')
res_ord = mod_ord.fit(method='bfgs')
print(res_ord.summary())

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import logistic

# Baseline probabilities (when all predictors = 0)
thresholds = [-np.inf, -3.253, 0.292, 0.255, 0.956, np.inf]
x = np.linspace(-5, 5, 1000)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Cumulative probabilities
ax1.set_title('Cumulative Probability Function')
for i in range(1, len(thresholds)):
    if i < len(thresholds)-1:
        prob = logistic.cdf(thresholds[i] - x)
        ax1.plot(x, prob, label=f'P(Y ≤ {i+2})')
ax1.set_xlabel('Linear Predictor Value')
ax1.set_ylabel('Cumulative Probability')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Category probabilities
ax2.set_title('Probability of Each Rating Category')
categories = []
for x_val in [-2, 0, 2]:  # Different predictor values
    probs = []
    for i in range(len(thresholds)-1):
        p_upper = logistic.cdf(thresholds[i+1] - x_val)
        p_lower = logistic.cdf(thresholds[i] - x_val)
        probs.append(p_upper - p_lower)
    categories.append(probs)

x_pos = np.arange(7)
width = 0.25
for i, (cat_probs, label) in enumerate(zip(categories, ['Low', 'Medium', 'High'])):
    ax2.bar(x_pos + i*width, cat_probs, width, label=f'{label} predictors')

ax2.set_xlabel('Rating')
ax2.set_ylabel('Probability')
ax2.set_xticks(x_pos + width)
ax2.set_xticklabels(['1', '2', '3', '4', '5', '6', '7'])
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.show()