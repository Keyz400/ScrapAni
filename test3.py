import subprocess
from bs4 import BeautifulSoup
import time

def fetch_page_with_curl(url):
    try:
        return subprocess.check_output(['curl', '-s', url], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching {url} with curl: {e}")
        return None

def get_seasons_and_episode_counts(series_url):
    html = fetch_page_with_curl(series_url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    season_dropdown = soup.find('div', class_='aa-drp choose-season')
    if not season_dropdown:
        print("Season dropdown not found.")
        return None
    
    # Known episode counts for "Bleach: Thousand-Year Blood War"
    # Adjust these based on actual data if different
    episode_counts = {'1': 13, '2': 13, '3': 14}  # Season 1: 13, Season 2: 13, Season 3: 14
    
    seasons = {}
    season_items = season_dropdown.find_all('li', class_='sel-temp')
    for item in season_items:
        season_num = item.find('a').get('data-season')
        if season_num in episode_counts:
            seasons[season_num] = episode_counts[season_num]
    
    return seasons

def scrape_mega_links(episode_url):
    html = fetch_page_with_curl(episode_url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    mega_links = []
    
    modal = soup.find('div', id='mdl-download')
    if modal:
        download_rows = modal.find_all('tr')
        for row in download_rows[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 4 and 'Mega' in cols[0].text:
                quality = cols[2].text.strip()
                link = cols[3].find('a')['href'].split(' class=')[0]
                mega_links.append({
                    'quality': quality,
                    'url': link
                })
    
    return mega_links if mega_links else None

def main():
    series_url = "https://anime-world.co/series/naruto/"
    print("Scraping Mega download links for all seasons...")
    
    seasons = get_seasons_and_episode_counts(series_url)
    if not seasons:
        print("Failed to fetch seasons.")
        return
    
    for season_num, ep_count in seasons.items():
        print(f"\nSeason {season_num}:")
        for ep_num in range(1, ep_count + 1):
            ep_id = f"{season_num}x{ep_num}"
            ep_url = f"https://anime-world.co/episode/naruto-{ep_id}/"
            print(f"\nEpisode {ep_id}:")
            mega_links = scrape_mega_links(ep_url)
            if mega_links:
                for link in mega_links:
                    print(f"- {link['quality']}: {link['url']}")
            else:
                print("- No Mega links found or page not available.")
            time.sleep(2)  # Rate limit to avoid overwhelming server

if __name__ == "__main__":
    main()
  
