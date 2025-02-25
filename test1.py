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

def scrape_episode_links(series_url):
    html = fetch_page_with_curl(series_url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    episodes = soup.find_all('article', class_=['post', 'dfx', 'fcl', 'episodes'])
    
    if not episodes:
        print("No episodes found. HTML structure mismatch.")
        print("Available article tags:", [tag.get('class') for tag in soup.find_all('article')[:5]])
        return None
    
    episode_links = {}
    for episode in episodes:
        ep_number = episode.find('span', class_='num-epi')
        ep_link = episode.find('a', class_='lnk-blk')
        
        if ep_number and ep_link:
            ep_num_text = ep_number.text.strip()
            ep_link_href = ep_link['href']
            episode_links[ep_num_text] = ep_link_href
    
    return episode_links if episode_links else None

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
                link = cols[3].find('a')['href'].split('"')[0]
                mega_links.append({
                    'quality': quality,
                    'url': link
                })
    
    return mega_links if mega_links else None

def main():
    series_url = "https://anime-world.co/series/naruto/"
    print("Scraping Mega download links...")
    episode_links = scrape_episode_links(series_url)
    
    if episode_links:
        for ep_num, ep_link in episode_links.items():
            print(f"\nEpisode {ep_num}:")
            mega_links = scrape_mega_links(ep_link)
            if mega_links:
                for link in mega_links:
                    print(f"- {link['quality']}: {link['url']}")
            else:
                print("- No Mega links found.")
            time.sleep(2)
    else:
        print("Failed to scrape episode list.")

if __name__ == "__main__":
    main()
  
