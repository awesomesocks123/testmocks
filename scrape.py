import requests
import re
from bs4 import BeautifulSoup

def extract_slug(url):
    match = re.search(r'leetcode\.com/problems/([\w-]+)/?', url)
    return match.group(1) if match else None

def fetch_problem_data(slug):
    url = "https://leetcode.com/graphql"
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://leetcode.com/problems/{slug}/",
        "User-Agent": "Mozilla/5.0"
    }

    query = """
    query getQuestionDetail($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        title
        content
        exampleTestcases
        difficulty
        likes
        dislikes
        hints
      }
    }
    """

    variables = {"titleSlug": slug}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)

    if response.status_code == 200:
        return response.json()['data']['question']
    else:
        raise Exception(f"Failed to fetch problem data (status {response.status_code})")

def save_to_txt(data, slug):
    # Convert HTML to plain text
    soup = BeautifulSoup(data['content'], 'html.parser')
    plain_description = soup.get_text()

    filename = f"scraped_problems.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Title: {data['title']}\n")
        f.write(f"Difficulty: {data['difficulty']}\n")
        f.write(f"Likes: {data['likes']}, Dislikes: {data['dislikes']}\n\n")
        f.write("Description:\n")
        f.write(plain_description + "\n\n")
        f.write("Example Testcases:\n")
        f.write(data.get('exampleTestcases', 'N/A') + "\n\n")
        f.write("Follow-up Questions / Hints:\n")
        f.write('\n'.join(data.get('hints', [])) or 'None')

    print(f"[+] Saved to {filename}")

def get_url():
    url = input("Paste the LeetCode problem URL: ").strip()
    slug = extract_slug(url)
    if not slug:
        print("Invalid LeetCode URL.")
        return

    try:
        problem_data = fetch_problem_data(slug)
        save_to_txt(problem_data, slug)
    except Exception as e:
        print(f"Error: {e}")
