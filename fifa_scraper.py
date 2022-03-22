import numpy as np
from bs4 import BeautifulSoup
import requests
import csv


def scraper():
    keys = ['Player Name', 'Edition', 'Overall Score', 'Predicted Score', 'Market Value', 'Weekly Salary', 'height',
            'Weight', 'Age', 'Preferred Foot', 'Ball Skills', 'Defence', 'Mental', 'Passing', 'Physical', 'Shooting',
            'Goalkeeping']
    base_url = 'https://www.fifaindex.com'
    url = base_url + '/players/{}/'  # creating url for primary pages
    page_no = 1
    # Write keys to top of file
    with open('fifa_index_players.csv', 'a', newline='', encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(keys)

    while True:
        web_page = url.format(page_no)
        page_res = requests.get(web_page)
        if page_res.status_code != 200:  # if maximum page exceeded, break out of loop
            break
        main_page = page_res.text
        main_soup = BeautifulSoup(main_page, 'html.parser')  # turn primary page into soup
        for tag in main_soup.find_all('td', attrs={'data-title': 'Name'}):  # iterate through each player on primary pages
            player_request = requests.get(base_url + str(tag.find('a')['href']))
            subpage = player_request.text
            soup = BeautifulSoup(subpage, 'html.parser')  # turn secondary page into soup
            nav = soup.find_all('nav')[1].contents[1].contents[3].contents[3] # find all drop down links for Fifa editions
            player_name = tag.find('a').contents[0]
            print(player_name)
            for attr in nav.contents:
                if attr != '\n':
                    edition = attr.contents[0]
                    # Get data from FIFA 17
                    if edition == 'FIFA 16':
                        break
                    # Ignore the World Cup edition
                    if edition != 'FIFA 18 WC':
                        player_url = base_url + str(attr['href'])
                        player_data = get_player_data(player_name, edition, player_url)
                        # Add each players data to file
                        if player_data is not None:
                            with open('fifa_index_players.csv', 'a', newline='', encoding="utf-8") as f:
                                w = csv.writer(f)
                                w.writerow(player_data.values())
        print(page_no)
        page_no += 1


def get_player_data(player_name, edition, player_url):
    player_request = requests.get(player_url)
    player_page = player_request.text
    soup = BeautifulSoup(player_page, 'html.parser')  # turn secondary page into soup

    overall_score = soup.find_all('span', class_='float-right')[0].contents[0].text
    predicted_score = soup.find_all('span', class_='float-right')[0].contents[2].text

    if soup.find_all('p', class_='data-currency data-currency-euro'):
        market_value = ''.join([i for i in soup.find_all('p', class_='data-currency data-currency-euro')[0].findNext().text if i.isdigit()])
        weekly_salary = ''.join([i for i in soup.find_all('p', class_='data-currency data-currency-euro')[1].findNext().text if i.isdigit()])
    else:
        market_value = np.nan
        weekly_salary = np.nan
    height = soup.find_all('span', class_="data-units data-units-metric")[0].text.split()[0]
    weight = soup.find_all('span', class_="data-units data-units-metric")[1].text.split()[0]
    age = soup.find(text='Age ').findNext().text
    preferred_foot = soup.find(text='Preferred Foot ').findNext().text

    ball_skills_stats = soup.find(text='Ball Skills').find_next().text.split('\n')[1:-1]
    ball_control = float(ball_skills_stats[0].split()[-1])
    dribbling = float(ball_skills_stats[1].split()[-1])
    ball_skills = np.mean([ball_control, dribbling])

    defence_stats = soup.find(text='Defence').find_next().text.split('\n')[1:-1]
    marking = float(defence_stats[0].split()[-1])
    slide_tackle = float(defence_stats[1].split()[-1])
    stand_tackle = float(defence_stats[2].split()[-1])
    defence = np.mean([marking, slide_tackle, stand_tackle])

    mental_stats = soup.find(text='Mental').find_next().text.split('\n')[1:-1]
    aggression = float(mental_stats[0].split()[-1])
    reactions = float(mental_stats[1].split()[-1])
    attack_position = float(mental_stats[2].split()[-1])
    interceptions = float(mental_stats[3].split()[-1])
    vision = float(mental_stats[4].split()[-1])
    composure = float(mental_stats[5].split()[-1])
    mental = np.mean([aggression, reactions, attack_position, interceptions, vision, composure])

    passing_stats = soup.find(text='Passing').find_next().text.split('\n')[1:-1]
    crossing = float(passing_stats[0].split()[-1])
    short_pass = float(passing_stats[1].split()[-1])
    long_pass = float(passing_stats[2].split()[-1])
    passing = np.mean([crossing, short_pass, long_pass])

    physical_stats = soup.find(text='Physical').find_next().text.split('\n')[1:-1]
    acceleration = float(physical_stats[0].split()[-1])
    stamina = float(physical_stats[1].split()[-1])
    strength = float(physical_stats[2].split()[-1])
    balance = float(physical_stats[3].split()[-1])
    sprint_speed = float(physical_stats[4].split()[-1])
    agility = float(physical_stats[5].split()[-1])
    jumping = float(physical_stats[6].split()[-1])
    physical = np.mean([acceleration, stamina, strength, balance, sprint_speed, agility, jumping])

    shooting_stats = soup.find(text='Shooting').find_next().text.split('\n')[1:-1]
    heading = float(shooting_stats[0].split()[-1])
    shot_power = float(shooting_stats[1].split()[-1])
    finishing = float(shooting_stats[2].split()[-1])
    long_shots = float(shooting_stats[3].split()[-1])
    curve = float(shooting_stats[4].split()[-1])
    fk_acc = float(shooting_stats[5].split()[-1])
    penalties = float(shooting_stats[6].split()[-1])
    volleys = float(shooting_stats[7].split()[-1])
    shooting = np.mean([heading, shot_power, finishing, long_shots, curve, fk_acc, penalties, volleys])

    goalkeeper_stats = soup.find(text='Goalkeeper').find_next().text.split('\n')[1:-1]
    gk_positioning = float(goalkeeper_stats[0].split()[-1])
    gk_diving = float(goalkeeper_stats[1].split()[-1])
    gk_handling = float(goalkeeper_stats[2].split()[-1])
    gk_kicking = float(goalkeeper_stats[3].split()[-1])
    gk_reflexes = float(goalkeeper_stats[4].split()[-1])
    goalkeeper = np.mean([gk_positioning, gk_diving, gk_handling, gk_kicking, gk_reflexes])

    player = {'Player Name': player_name, 'Edition': edition,
              'Overall Score': overall_score, 'Predicted Score': predicted_score,
              'Market Value': market_value,
              'Weekly Salary': weekly_salary, 'height': height,
              'Weight': weight, 'Age': age,
              'Preferred Foot': preferred_foot,
              'Ball Skills': ball_skills, 'Defence': defence,
              'Mental': mental, 'Passing': passing, 'Physical': physical,
              'Shooting': shooting,
              'Goalkeeping': goalkeeper}
    return player


if __name__ == '__main__':
    scraper()
