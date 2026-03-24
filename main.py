import sys
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from crew import PMCrew

if __name__ == "__main__":
    crew = PMCrew()
    crew.run()
