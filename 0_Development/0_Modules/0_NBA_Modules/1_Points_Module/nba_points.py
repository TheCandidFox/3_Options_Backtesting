import os
import pytz
from datetime import datetime
import matplotlib.pyplot as plt
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# ==== USER CONFIGURATION ====
PLAYER_NAME = "Draymond Green"
POINTS_LINE = 9.5
SEASON_SELECTION = '2024-25'
OUTPUT_FOLDER = "./1_Output_Folder"
PROP_LABEL = "Point-"
MAX_GAMES = 10
COLOR_CYCLE = ['#ffffcc', '#ffe0b2', '#f8bbd0', '#c8e6c9', '#bbdefb', '#ffffcc']  # Yellow, Orange, Pink, Green, Blue, Yellow (repeats)
# ============================

# Helper to increment filename counter
def get_next_filename_index(output_folder, base_name):
    existing = [f for f in os.listdir(output_folder) if f.endswith(".png") and base_name in f]
    return len(existing)

# Step 1: Get Player ID
player = [p for p in players.get_players() if p['full_name'] == PLAYER_NAME][0]
player_id = player['id']

# Step 2: Get Game Logs for Past 3 Seasons (Regular + Playoffs)
df_all = []

for season_type in ['Regular Season', 'Playoffs']:
    gl = playergamelog.PlayerGameLog(player_id=player_id, season=SEASON_SELECTION, season_type_all_star=season_type)
    df = gl.get_data_frames()[0]
    df['SEASON'] = SEASON_SELECTION
    df['SEASON_TYPE'] = season_type
    df_all.append(df)


# Step 3: Combine all game logs
df_all = pd.concat(df_all, ignore_index=True)
df_all['GAME_DATE'] = pd.to_datetime(df_all['GAME_DATE'])
df_all.sort_values('GAME_DATE', inplace=True)

# Step 4: Create regular season stats
df_regular = df_all[(df_all['SEASON_TYPE'] == 'Regular Season') & (df_all['SEASON'] == SEASON_SELECTION)]
regular_avg = df_regular['PTS'].mean()
home_games = df_regular[df_regular['MATCHUP'].str.contains("vs.")]
away_games = df_regular[df_regular['MATCHUP'].str.contains("@")]
home_avg = home_games['PTS'].mean()
away_avg = away_games['PTS'].mean()
hit_rate = (df_regular['PTS'] > POINTS_LINE).mean() * 100

# Step 4.5: Find Dynamic Games Played
# Dynamically calculate how many regular season games the team has played
# Assumes 'MATCHUP' is in format 'BOS vs. MIA' or 'BOS @ MIA'
team_code = df_regular['MATCHUP'].iloc[0].split(" ")[0]
team_games_played = df_regular[df_regular['MATCHUP'].str.startswith(team_code)]
team_game_dates = team_games_played['GAME_DATE'].dt.date.unique()
REGULAR_SEASON_GAME_TOTAL = len(team_game_dates)

games_played = len(df_regular)
avg_minutes = pd.to_numeric(df_regular['MIN'], errors='coerce').fillna(0).sum() / games_played


# Step 5: Rolling last 10 games logic
last_games = df_all.tail(MAX_GAMES).copy()
last_games = last_games[['GAME_DATE', 'PTS', 'MIN', 'MATCHUP', 'SEASON_TYPE', 'WL']]
last_games['MIN'] = pd.to_numeric(last_games['MIN'], errors='coerce').fillna(0)
last_games['PTS'] = pd.to_numeric(last_games['PTS'], errors='coerce').fillna(0)

# Convert to CDT
utc_times = last_games['GAME_DATE'].dt.tz_localize('UTC')
cdt = pytz.timezone('America/Chicago')
cdt_times = utc_times.dt.tz_convert(cdt)
last_games['CDT_TIME'] = cdt_times.dt.strftime("%b %d %Y\n%I:%M %p")

# Extract labels and color codes
labels, color_map = [], {}
opponent_color_index = -1
prev_team = None

for _, row in last_games.iterrows():
    matchup = row['MATCHUP']
    is_home = "vs." in matchup
    parts = matchup.split(" ")
    player_team = parts[0]
    opponent = parts[-1]
    key = opponent

    if key != prev_team:
        opponent_color_index += 1
    color = COLOR_CYCLE[opponent_color_index % len(COLOR_CYCLE)]
    prev_team = key

    location = "Home" if is_home else "Away"
    label = f"{player_team} vs. {opponent}\n{location}\n{row['CDT_TIME']}"
    labels.append(label)
    color_map[label] = color

# Step 6: Plot chart
fig, ax1 = plt.subplots(figsize=(14, 6))
bar_width = 0.35
x = range(len(last_games))

# Plot Points
bars1 = ax1.bar([i - bar_width/2 for i in x], last_games['PTS'], width=bar_width, label='Points', color='skyblue')
ax1.set_ylabel("Points")
ax1.set_ylim(0, max(40, last_games['PTS'].max() + 5))
ax1.axhline(POINTS_LINE, color='red', linestyle='--', label=f'Line: {POINTS_LINE}')
ax1.set_yticks(range(0, 46, 5))

# Plot Minutes
ax2 = ax1.twinx()
bars2 = ax2.bar([i + bar_width/2 for i in x], last_games['MIN'], width=bar_width, label='Minutes', color='orange')
ax2.set_ylabel("Minutes Played")
ax2.set_ylim(0, 50)
ax2.set_yticks(range(0, 55, 5))

# Set x-axis labels with colored backgrounds
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=45, ha='right')
for tick_label, label in zip(ax1.get_xticklabels(), labels):
    tick_label.set_backgroundcolor(color_map[label])

# Add legends
fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.95))

# Step 7: Save figure
index = get_next_filename_index(OUTPUT_FOLDER, f"{PLAYER_NAME.split()[1]}_{PROP_LABEL}")
filename = f"{index}_{PLAYER_NAME.split()[1]}_{PROP_LABEL}_Analysis.png"
plt.tight_layout()
#plt.savefig(os.path.join(OUTPUT_FOLDER, filename))
plt.show()

# Step 8: Print summary
percent_played = (games_played / REGULAR_SEASON_GAME_TOTAL) * 100

print(f"\n📊 Regular Season Stats for {PLAYER_NAME}")
print(f"Regulation Games: {REGULAR_SEASON_GAME_TOTAL} | Games Played: {games_played} | Percentage: {percent_played:.2f}%")
print(f"Average Minutes Played per Game: {avg_minutes:.2f}")

print(f"\nAverage Points: {regular_avg:.2f}")
print(f"Home Avg: {home_avg:.2f} | Away Avg: {away_avg:.2f}")
print(f"Hit Rate vs {POINTS_LINE}: {hit_rate:.2f}%")

print(f"\nLast {MAX_GAMES} Games Used for Chart (includes playoffs + regular season):")
print(last_games[['GAME_DATE', 'PTS', 'MIN', 'MATCHUP']])
print(f"\n✅ Chart saved to: {filename}")