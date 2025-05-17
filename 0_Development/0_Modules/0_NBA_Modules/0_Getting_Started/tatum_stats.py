from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# Find Jayson Tatum's player ID
tatum = [p for p in players.get_players() if p['full_name'] == 'Jayson Tatum'][0]
player_id = tatum['id']

# Pull regular season game logs for 2023-24
game_log = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25', season_type_all_star='Regular Season')
df = game_log.get_data_frames()[0]

# Keep only relevant columns
df = df[['GAME_DATE', 'MIN', 'PTS', 'REB', 'FG3A', 'STL']].copy()
df['MIN'] = pd.to_numeric(df['MIN'], errors='coerce')

# Calculate stats
games_played = len(df)
avg_minutes = df['MIN'].mean()
minutes_percent = round((avg_minutes / 48) * 100, 1)

# Display output
print(f"\n🧾 Jayson Tatum - 2023-24 Season Summary")
print(f"Games Played: {games_played}")
print(f"Average Minutes per Game: {avg_minutes:.2f} min ({minutes_percent:.1f}% of game time)")
print("\nSample Stats:\n")
print(df.head(10))  # Show first 10 games as a preview 
