# Robust full cell: normalise column names, compute metrics, and plot 3 graphs
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load your dataset
df = pd.read_csv("FCS1_Team2_Joshua.csv")

# --- 0. Normalize column names so code is case-insensitive ---
df.columns = df.columns.str.strip().str.lower()

# --- 1. CGPA balance within tutorials ---
team_means = df.groupby(['tutorial', 'team'])['cgpa'].mean().reset_index()
cgpa_balance = team_means.groupby('tutorial')['cgpa'].std().reset_index(name='std_cgpa_balance')

plt.figure(figsize=(12,5))
sns.barplot(data=cgpa_balance, x='tutorial', y='std_cgpa_balance', color='skyblue')
plt.title("CGPA Equality Within Tutorials (Lower SD = More Equal)")
plt.xlabel("Tutorial")
plt.ylabel("Standard Deviation of Team Mean CGPA")
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# --- 2. Gender balance within tutorials ---
gender_props = (
    df.assign(is_female=df['gender'].str.lower().eq('female').astype(int))
      .groupby(['tutorial','team'])['is_female']
      .mean()
      .reset_index(name='prop_female')
)
gender_balance = gender_props.groupby('tutorial')['prop_female'].std().reset_index(name='std_gender_balance')

plt.figure(figsize=(12,5))
sns.barplot(data=gender_balance, x='tutorial', y='std_gender_balance', color='lightgreen')
plt.title("Gender Equality Within Tutorials (Lower SD = More Equal)")
plt.xlabel("Tutorial")
plt.ylabel("Standard Deviation of Female Proportion")
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# --- 3. School diversity within tutorials (FIXED - BETTER METRIC) ---
# Count unique schools per team
school_diversity = (
    df.groupby(['tutorial', 'team'])['school']
    .nunique()
    .reset_index(name='num_schools')
)

# Average number of different schools per team in each tutorial
school_summary = (
    school_diversity
    .groupby('tutorial')['num_schools']
    .mean()
    .reset_index(name='avg_schools_per_team')
)

plt.figure(figsize=(12,5))
sns.barplot(data=school_summary, x='tutorial', y='avg_schools_per_team', color='orange')
plt.title("School Diversity Within Tutorials (Higher = More Diverse)")
plt.xlabel("Tutorial")
plt.ylabel("Average Number of Different Schools Per Team")
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()