import urllib.request
import json
import os
import re

TOKEN = os.environ.get("GH_PAT")
USERNAME = "CodeWithBasu"

# Fetch data using GitHub's GraphQL API
query = """
{
  user(login: "%s") {
    contributionsCollection {
      contributionCalendar {
        totalContributions
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER) {
      totalDiskUsage
      nodes {
        isPrivate
      }
    }
  }
}
""" % USERNAME

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query}).encode("utf-8"),
    headers={"Authorization": f"Bearer {TOKEN}"}
)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())['data']['user']
        
    contribs = data['contributionsCollection']['contributionCalendar']['totalContributions']
    repos = data['repositories']['nodes']
    
    public_repos = sum(1 for r in repos if not r['isPrivate'])
    private_repos = sum(1 for r in repos if r['isPrivate'])
    disk_usage_mb = round(data['repositories']['totalDiskUsage'] / 1024, 1)

    # Format the Markdown
    stats_text = f"""### 🐱 My GitHub Data
> 📦 {disk_usage_mb} MB Used in GitHub's Storage
> <br>
> 🏆 {contribs} Contributions this Year
> <br>
> 🚫 Not Opted to Hire
> <br>
> 📜 {public_repos} Public Repositories
> <br>
> 🔑 {private_repos} Private Repositories"""

    # Inject into README
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    new_readme = re.sub(
        r"<!-- START_STATS -->.*<!-- END_STATS -->",
        f"<!-- START_STATS -->\n{stats_text}\n<!-- END_STATS -->",
        readme,
        flags=re.DOTALL
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)
        
    print("README updated successfully!")
except Exception as e:
    print(f"Error fetching data: {e}")
