import subprocess
from bs4 import BeautifulSoup
import re
import time

def fetch_page_with_curl(url):
    try:
        return subprocess.check_output(['curl', '-s', url], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching {url} with curl: {e}")
        return None

def search_anime(query):
    search_url = f"https://anime-world.co/?s={query.replace(' ', '+')}"
    html = fetch_page_with_curl(search_url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    # Assuming search results are in <article> tags with class 'post'
    for article in soup.find_all('article', class_='post'):
        title_elem = article.find('h2', class_='entry-title')
        link_elem = article.find('a', class_='lnk-blk')
        if title_elem and link_elem:
            results.append({
                'title': title_elem.text.strip(),
                'url': link_elem['href']
            })
    
    return results if results else None

def get_seasons_and_episodes(series_url):
    html = fetch_page_with_curl(series_url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    seasons = {}
    season_dropdown = soup.find('div', class_='aa-drp choose-season')
    if season_dropdown:
        season_items = season_dropdown.find_all('li', class_='sel-temp')
        for item in season_items:
            season_num = item.find('a').get('data-season')
            seasons[season_num] = []
    
    # Get episodes from the current season loaded
    episodes = soup.find_all('article', class_=['post', 'dfx', 'fcl', 'episodes'])
    for ep in episodes:
        ep_number = ep.find('span', class_='num-epi')
        ep_link = ep.find('a', class_='lnk-blk')
        if ep_number and ep_link:
            season = ep_number.text.strip().split('x')[0]
            if season in seasons:
                seasons[season].append({
                    'ep_num': ep_number.text.strip(),
                    'url': ep_link['href']
                })
    
    # Infer remaining episodes for other seasons (assuming 13-14 episodes)
    for season in seasons:
        if not seasons[season]:  # If no episodes found statically
            ep_count = 13 if season in ['1', '2'] else 14  # Adjust as needed
            for ep in range(1, ep_count + 1):
                ep_id = f"{season}x{ep}"
                seasons[season].append({
                    'ep_num': ep_id,
                    'url': f"https://anime-world.co/episode/bleach-thousand-year-blood-war-{ep_id}/"
                })
    
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
        for row in download_rows[1:]:  # Skip header
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
    print("Anime Mega Download Link Extractor")
    query = input("Enter anime name to search: ").strip()
    
    # Search for anime
    results = search_anime(query)
    if not results:
        print("No results found or search failed.")
        return
    
    # Display search results
    print("\nSearch Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']} ({result['url']})")
    
    # User selects result
    while True:
        try:
            choice = int(input("\nSelect anime by number: "))
            if 1 <= choice <= len(results):
                selected_series = results[choice - 1]
                break
            print(f"Please enter a number between 1 and {len(results)}.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\nFetching episodes for: {selected_series['title']}")
    seasons = get_seasons_and_episodes(selected_series['url'])
    if not seasons:
        print("Failed to fetch seasons or episodes.")
        return
    
    # Display all episodes
    print("\nAvailable Episodes:")
    for season, episodes in seasons.items():
        print(f"\nSeason {season}:")
        for i, ep in enumerate(episodes, 1):
            print(f"{i}. Episode {ep['ep_num']}")
    
    # User selects episodes
    while True:
        ep_choice = input("\nEnter episode number to download (e.g., 1 for 1x1, or 'q' to quit): ").strip().lower()
        if ep_choice == 'q':
            break
        
        try:
            ep_idx = int(ep_choice) - 1
            flat_episodes = [ep for eps in seasons.values() for ep in eps]
            if 0 <= ep_idx < len(flat_episodes):
                selected_ep = flat_episodes[ep_idx]
                print(f"\nFetching Mega links for Episode {selected_ep['ep_num']}:")
                mega_links = scrape_mega_links(selected_ep['url'])
                if mega_links:
                    for link in mega_links:
                        print(f"- {link['quality']}: {link['url']}")
                else:
                    print("- No Mega links found or page not available.")
            else:
                print(f"Please enter a number between 1 and {len(flat_episodes)}.")
        except ValueError:
            print("Please enter a valid episode number or 'q' to quit.")
        time.sleep(1)

if __name__ == "__main__":
    main()
