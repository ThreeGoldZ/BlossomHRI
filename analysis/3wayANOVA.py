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

# Print first 3 rows of each DataFrame
print('Valence Partner DataFrame:')
print(valence_partner_df.head(30))
print(valence_partner_df.__len__())

# Make sure categorical variables are treated as such
valence_partner_df['robot'] = valence_partner_df['robot'].astype('category')
valence_partner_df['touch'] = valence_partner_df['touch'].astype('category')
valence_partner_df['emotion'] = valence_partner_df['emotion'].astype('category')

# Three-way ANOVA model
model = ols('value ~ C(robot) * C(touch) * C(emotion)', data=valence_partner_df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)

print("=== PARTNER VALENCE ANOVA ===")
print(anova_table)

# Post-hoc analysis for partner valence
print("\n=== POST-HOC ANALYSIS FOR PARTNER VALENCE ===")

# Create interaction groups for post-hoc
valence_partner_df['robot_touch'] = valence_partner_df['robot'].astype(str) + '_' + valence_partner_df['touch'].astype(str)
valence_partner_df['robot_emotion'] = valence_partner_df['robot'].astype(str) + '_' + valence_partner_df['emotion'].astype(str)
valence_partner_df['touch_emotion'] = valence_partner_df['touch'].astype(str) + '_' + valence_partner_df['emotion'].astype(str)
valence_partner_df['robot_touch_emotion'] = valence_partner_df['robot'].astype(str) + '_' + valence_partner_df['touch'].astype(str) + '_' + valence_partner_df['emotion'].astype(str)

# Post-hoc for main effects
print("\n--- Robot Effect ---")
tukey_robot = pairwise_tukeyhsd(valence_partner_df['value'], valence_partner_df['robot'])
print(tukey_robot)

print("\n--- Touch Effect ---")
tukey_touch = pairwise_tukeyhsd(valence_partner_df['value'], valence_partner_df['touch'])
print(tukey_touch)

print("\n--- Emotion Effect ---")
tukey_emotion = pairwise_tukeyhsd(valence_partner_df['value'], valence_partner_df['emotion'])
print(tukey_emotion)

# Post-hoc for two-way interactions
print("\n--- Robot x Touch Interaction ---")
tukey_robot_touch = pairwise_tukeyhsd(valence_partner_df['value'], valence_partner_df['robot_touch'])
print(tukey_robot_touch)

print("\n--- Robot x Emotion Interaction ---")
tukey_robot_emotion = pairwise_tukeyhsd(valence_partner_df['value'], valence_partner_df['robot_emotion'])
print(tukey_robot_emotion)

print("\n--- Touch x Emotion Interaction ---")
tukey_touch_emotion = pairwise_tukeyhsd(valence_partner_df['value'], valence_partner_df['touch_emotion'])
print(tukey_touch_emotion)

# Post-hoc for three-way interaction
print("\n--- Robot x Touch x Emotion Interaction ---")
tukey_robot_touch_emotion = pairwise_tukeyhsd(valence_partner_df['value'], valence_partner_df['robot_touch_emotion'])
print(tukey_robot_touch_emotion)

#run the same model for arousal and confidence
arousal_partner_df['robot'] = arousal_partner_df['robot'].astype('category')
arousal_partner_df['touch'] = arousal_partner_df['touch'].astype('category')
arousal_partner_df['emotion'] = arousal_partner_df['emotion'].astype('category')
model = ols('value ~ C(robot) * C(touch) * C(emotion)', data=arousal_partner_df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

confidence_partner_df['robot'] = confidence_partner_df['robot'].astype('category')
confidence_partner_df['touch'] = confidence_partner_df['touch'].astype('category')
confidence_partner_df['emotion'] = confidence_partner_df['emotion'].astype('category')
model = ols('value ~ C(robot) * C(touch) * C(emotion)', data=confidence_partner_df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

valence_self_df['robot'] = valence_self_df['robot'].astype('category')
valence_self_df['touch'] = valence_self_df['touch'].astype('category')
valence_self_df['emotion'] = valence_self_df['emotion'].astype('category')
model = ols('value ~ C(robot) * C(touch) * C(emotion)', data=valence_self_df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

arousal_self_df['robot'] = arousal_self_df['robot'].astype('category')
arousal_self_df['touch'] = arousal_self_df['touch'].astype('category')
arousal_self_df['emotion'] = arousal_self_df['emotion'].astype('category')
model = ols('value ~ C(robot) * C(touch) * C(emotion)', data=arousal_self_df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

confidence_self_df['robot'] = confidence_self_df['robot'].astype('category')
confidence_self_df['touch'] = confidence_self_df['touch'].astype('category')
confidence_self_df['emotion'] = confidence_self_df['emotion'].astype('category')
model = ols('value ~ C(robot) * C(touch) * C(emotion)', data=confidence_self_df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

# If you haven't already, ensure these are categorical for better plotting
valence_partner_df['robot'] = valence_partner_df['robot'].astype('category')
valence_partner_df['touch'] = valence_partner_df['touch'].astype('category')
valence_partner_df['timepoint'] = valence_partner_df['emotion'].astype('category')

plt.figure(figsize=(14, 6))
sns.boxplot(
    data=valence_partner_df,
    x='emotion',
    y='value',
    hue='robot',
    palette='Set2',
    dodge=True
)
plt.title('Valence by Timepoint and Robot (Touch as Facet)')
plt.xlabel('Timepoint')
plt.ylabel('Valence')

# Facet by touch
g = sns.catplot(
    data=valence_partner_df,
    x='emotion',
    y='value',
    hue='robot',
    col='touch',
    kind='box',
    palette='Set2',
    height=5,
    aspect=1
)
g.fig.subplots_adjust(top=0.85)
g.fig.suptitle('Valence by Timepoint, Robot, and Touch')
plt.show()
