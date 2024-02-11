import os
import subprocess
import requests
import tempfile
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not VERCEL_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Environment variables for VERCEL_TOKEN or OPENAI_API_KEY are not set.")

class PortfolioCreator:
    def __init__(self, vercel_token: str, openai_api_key: str):
        self.vercel_token = vercel_token
        self.openai_api_key = openai_api_key

    def deploy_to_vercel(self, html_content: str, project_name: str):
        """Deploy website content to Vercel."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / project_name
            os.makedirs(project_dir)

            with open(project_dir / "index.html", "w") as file:
                file.write(html_content)

            vercel_config = {
                "name": project_name,
                "version": 2,
                "builds": [{"src": "index.html", "use": "@vercel/static"}]
            }

            with open(project_dir / "vercel.json", "w") as file:
                json.dump(vercel_config, file)

            cmd = ["vercel", "--token", self.vercel_token, "-y", "--prod"]
            result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)

            if result.returncode == 0:
                print("Deployment successful!")
                print(f"Your website is live at: {result.stdout.strip()}")
            else:
                print("Deployment failed:", result.stderr)

    def generate_website_content(self, github_profile: dict) -> str:
        """Generate HTML content for the portfolio website."""
        prompt = f"""Create a professional, elegant, and responsive portfolio website for a developer.
        The website should include a navigation bar, a header section with the user's name and a brief introduction,
        an About Me section with the user's profile image and a description, a Projects section showcasing the user's work,
        and a Contact section with a form. It should also include a footer with copyright information.
        The design should be modern, with a clean layout, appealing visuals, and subtle animations.
        Include the following information from the provided GitHub profile:
        ---
        {json.dumps(github_profile, indent=2)}
        """

        chat = ChatOpenAI(openai_api_key=self.openai_api_key, temperature=0.2, max_tokens=2500)

        messages = [
            SystemMessage(content="You are an expert web designer. Generate HTML and CSS code that is professional, aesthetically pleasing, and user-friendly."),
            HumanMessage(content=prompt)
        ]

        response = chat(messages)
        return response.content

    def create_portfolio_for_github_user(self, username: str):
        """Create and deploy a portfolio website for a GitHub user."""
        response = requests.get(f"https://api.github.com/users/{username}")
        if response.status_code != 200:
            print(f"Error fetching GitHub profile data. Status code: {response.status_code}")
            return

        github_profile_data = response.json()
        html_content = self.generate_website_content(github_profile_data)
        project_name = f"{username}-portfolio"
        self.deploy_to_vercel(html_content, project_name)

if __name__ == "__main__":
    github_username = "add_your_username"
    portfolio_creator = PortfolioCreator(VERCEL_TOKEN, OPENAI_API_KEY)
    portfolio_creator.create_portfolio_for_github_user(github_username)
