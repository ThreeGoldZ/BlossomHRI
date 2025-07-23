from ast import mod
import json
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

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
    print(user_id)
    for cond, cond_data in user['conditions'].items():
        robot, touch = parse_condition(cond)
        print(cond)
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

# Print first 3 rows of each DataFrame
print('arousal Partner DataFrame:')
print(valence_partner_df.head(300))
#print(arousal_partner_df.__len__())


# 1. Plot value over user_id
plt.plot(valence_partner_df['user_id'], valence_partner_df['value'], marker='o')
plt.xlabel('User ID')
plt.ylabel('Value')
plt.title('Value over User ID')
plt.show()

# 2. Calculate difference between consecutive values
valence_partner_df['value_diff'] = valence_partner_df['value'].diff()
print(valence_partner_df[['user_id', 'value', 'value_diff']])

# 3. Group by emotion (or any other column) and plot mean value
grouped = valence_partner_df.groupby('emotion')['value'].mean()
grouped.plot(kind='bar')
plt.xlabel('Emotion')
plt.ylabel('Mean Value')
plt.title('Mean Value by Emotion')
plt.show()

# Assume valence_partner_df is your DataFrame

# Choose the column to group by (must have 16 unique values)
group_col = 'user_id'  # Change to 'robot', 'touch', or 'emotion' if needed

unique_groups = valence_partner_df[group_col].unique()[:16]  # Ensure only 16 groups
fig, axes = plt.subplots(4, 4, figsize=(16, 12), sharey=True)

for i, group in enumerate(unique_groups):
    ax = axes[i // 4, i % 4]
    group_df = valence_partner_df[valence_partner_df[group_col] == group]
    ax.plot(group_df.index, group_df['value'], marker='o')
    ax.set_title(f"{group_col}: {group}")
    ax.set_xlabel('Index')
    ax.set_ylabel('arousal')

plt.tight_layout()
plt.show()

# Create a 'condition' column
def get_condition(row):
    if row['robot'] == 1 and row['touch'] == 1:
        return 'B+T+'
    elif row['robot'] == 1 and row['touch'] == 0:
        return 'B+T-'
    elif row['robot'] == 0 and row['touch'] == 1:
        return 'B-T+'
    else:
        return 'B-T-'

valence_partner_df['condition'] = valence_partner_df.apply(get_condition, axis=1)

group_col = 'user_id'
unique_groups = valence_partner_df[group_col].unique()[:16]
fig, axes = plt.subplots(4, 4, figsize=(16, 12), sharey=True)

# Define background colors for each condition
bg_colors = {
    'B+T+': 'blue',
    'B+T-': 'green',
    'B-T+': 'yellow',
    'B-T-': 'white'  # or any other color you want for this condition
}

for i, group in enumerate(unique_groups):
    ax = axes[i // 4, i % 4]
    group_df = valence_partner_df[valence_partner_df[group_col] == group].reset_index()
    x = group_df.index
    y = group_df['value']
    cond = group_df['condition']

    # Draw background color bands for each contiguous region of the same condition
    for condition, color in bg_colors.items():
        mask = cond == condition
        indices = np.where(mask)[0]
        if len(indices) > 0:
            splits = np.split(indices, np.where(np.diff(indices) != 1)[0]+1)
            for region in splits:
                ax.axvspan(region[0]-0.5, region[-1]+0.5, color=color, alpha=0.2 if color != 'white' else 0)

    # Plot the black line for all values
    ax.plot(x, y, color='black', marker='o')
    ax.set_title(f"{group_col}: {group}")
    ax.set_xlabel('Index')
    ax.set_ylabel('Arousal')

plt.tight_layout()
plt.show()