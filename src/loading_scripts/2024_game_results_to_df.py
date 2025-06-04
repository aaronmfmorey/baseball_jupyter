from bs4 import BeautifulSoup
import re
import pandas as pd

shortcode_to_team = {
    "ARI": "Arizona Diamondbacks",
    "ATL": "Atlanta Braves",
    "BAL": "Baltimore Orioles",
    "BOS": "Boston Red Sox",
    "CHC": "Chicago Cubs",
    "CHW": "Chicago White Sox",
    "CIN": "Cincinnati Reds",
    "CLE": "Cleveland Guardians",
    "COL": "Colorado Rockies",
    "DET": "Detroit Tigers",
    "HOU": "Houston Astros",
    "KCR": "Kansas City Royals",
    "LAA": "Los Angeles Angels",
    "LAD": "Los Angeles Dodgers",
    "MIA": "Miami Marlins",
    "MIL": "Milwaukee Brewers",
    "MIN": "Minnesota Twins",
    "NYM": "New York Mets",
    "NYY": "New York Yankees",
    "OAK": "Oakland Athletics",
    "PHI": "Philadelphia Phillies",
    "PIT": "Pittsburgh Pirates",
    "SDP": "San Diego Padres",
    "SEA": "Seattle Mariners",
    "SFG": "San Francisco Giants",
    "STL": "St. Louis Cardinals",
    "TBR": "Tampa Bay Rays",
    "TEX": "Texas Rangers",
    "TOR": "Toronto Blue Jays",
    "WSN": "Washington Nationals"
}

team_to_shortcode = {v: k for k, v in shortcode_to_team.items()}

def parse_team_from_anchor(anchor):
    return anchor['href'].split('/')[2]

# Formula per Wikipedia: https://en.wikipedia.org/wiki/Pythagorean_expectation
def pythag_wins(runs_scored, runs_allowed, games_played):
    return 1 / (1 + ((runs_allowed / runs_scored) ** 1.83)) * games_played

# I copied this straight from the source of https://www.baseball-reference.com/leagues/majors/2024-schedule.shtml
with open('data/2024_game_results.html') as file:
    soup = BeautifulSoup(file, features='html.parser')

games = soup.find_all('p', class_='game')

run_differentials = {}
skeleton = {
            'games': 0,
            'rs': 0,
            'ra': 0,
            'diff': 0,
            'rs_blowout4': 0,
            'ra_blowout4': 0,
            'ra_blowout5': 0,
            'rs_blowout5': 0
        }

i = 1
for g in games:
    # for g in games:
    game_soup = BeautifulSoup(str(g), features='html.parser')
    game_anchors = game_soup.find_all('a')
    home_team = parse_team_from_anchor(game_anchors[0])
    away_team = parse_team_from_anchor(game_anchors[1])
    scores = re.findall(r'\((\d+)\)', game_soup.text)
    home_score = int(scores[0])
    away_score = int(scores[1])
    home_differential = home_score - away_score

    if not home_team in run_differentials:
        run_differentials[home_team] = skeleton.copy()

    if not away_team in run_differentials:
        run_differentials[away_team] = skeleton.copy()

    # print(f'{home_team} {home_score} - {away_team} {away_score}')
    run_differentials[home_team]['games'] += 1
    run_differentials[away_team]['games'] += 1
    run_differentials[home_team]['rs'] = run_differentials[home_team]['rs'] + home_score
    run_differentials[home_team]['ra'] = run_differentials[home_team]['ra'] + away_score
    run_differentials[away_team]['rs'] = run_differentials[away_team]['rs'] + away_score
    run_differentials[away_team]['ra'] = run_differentials[away_team]['ra'] + home_score
    # run_differentials[home_team]['diff_blowout4'] = run_differentials[home_team]['diff_blowout4'] + max(4,home_score - away_score)
    # run_differentials[away_team]['diff_blowout4'] = run_differentials[away_team]['diff_blowout4'] + max(4,away_score - home_score)
    # run_differentials[home_team]['diff_blowout5'] = run_differentials[home_team]['diff_blowout4'] + max(5,home_score - away_score)
    # run_differentials[away_team]['diff_blowout5'] = run_differentials[away_team]['diff_blowout4'] + max(5,away_score - home_score)
    # if home_team == 'LAD':
    #     print(f'{i} {run_differentials['LAD']}')
    #     i+=1

for team_id, team_stats in run_differentials.items():
    # print(team_id)
    run_differentials[team_id]['pythag'] = pythag_wins(team_stats['rs'], team_stats['ra'], team_stats['games'])

# CITE: https://www.baseball-reference.com/leagues/majors/2024-standings.shtml
actual_team_results = pd.read_csv('data/2024_team_results.csv')

for row in actual_team_results.itertuples():
    print(row)
    # Don't process the last "Average" row
    if row.Tm == 'Average':
        continue
    team_shortcode = team_to_shortcode[row.Tm]
    # print(team_shortcode)
    rd = run_differentials[team_shortcode]
    rd['actual_wins'] = row.W

# print(run_differentials)
df = pd.DataFrame.from_dict(run_differentials, orient='index')
print(df)
print(df[['pythag', 'actual_wins']].corr())