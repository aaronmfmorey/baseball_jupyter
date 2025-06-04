from bs4 import BeautifulSoup
import re
import pandas as pd

def parse_team_from_anchor(anchor):
    return anchor['href'].split('/')[2]

# I copied this straight from the source of https://www.baseball-reference.com/leagues/majors/2024-schedule.shtml
with open('data/2024_game_results.html') as file:
    soup = BeautifulSoup(file, features='html.parser')

games = soup.find_all('p', class_='game')

run_differentials = {}
skeleton = {
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
        run_differentials[home_team] = skeleton

    if not away_team in run_differentials:
        run_differentials[away_team] = skeleton

    # print(f'{home_team} {home_score} - {away_team} {away_score}')
    run_differentials[home_team]['rs'] = run_differentials[home_team]['rs'] + home_score
    run_differentials[home_team]['ra'] = run_differentials[home_team]['ra'] + away_score
    run_differentials[away_team]['rs'] = run_differentials[away_team]['rs'] + away_score
    run_differentials[away_team]['ra'] = run_differentials[away_team]['ra'] + home_score
    # run_differentials[home_team]['diff_blowout4'] = run_differentials[home_team]['diff_blowout4'] + max(4,home_score - away_score)
    # run_differentials[away_team]['diff_blowout4'] = run_differentials[away_team]['diff_blowout4'] + max(4,away_score - home_score)
    # run_differentials[home_team]['diff_blowout5'] = run_differentials[home_team]['diff_blowout4'] + max(5,home_score - away_score)
    # run_differentials[away_team]['diff_blowout5'] = run_differentials[away_team]['diff_blowout4'] + max(5,away_score - home_score)
    if home_team == 'LAD':
        print(f'{i} {run_differentials['LAD']}')
        i+=1

# print(run_differentials)
# df = pd.DataFrame(run_differentials)
# print(df.T.to_string())