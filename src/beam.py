import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

from calc import BeamCalcTool

load_dotenv()

openai_api_version = os.environ.get('AZURE_OPENAI_VERSION')
api_key = os.environ.get('AZURE_OPENAI_KEY')
azure_endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT')

search_tool = DuckDuckGoSearchRun()
calc_tool = BeamCalcTool()

openai_llm = ChatOpenAI(model='gpt-3.5-turbo')
azure_llm = AzureChatOpenAI(
    api_key=api_key,
    api_version=openai_api_version,
    azure_endpoint=azure_endpoint,
    azure_deployment=azure_endpoint,
    model='gpt-35-turbo-eastus-unfiltered',
    temperature=0,
    verbose=True
)

problem = """A 400mm x 600mm concrete beam with compressive strength of 27 MPa needs to carry a
bending moment of 160kNm and shear force of 85kN. What is the required reinforcements for a steel
with yield strength of 414 MPa?"""

# Define your agents with roles and goals
engineer = Agent(
    llm=openai_llm,
    role='Structural Engineer Designer',
    goal="""You need to design an efficient reinforced-concrete beam by determining its 
    required reinforcements based on given loads.""",
    backstory="""You are a practicing structural engineer with decades of experience in designing
    reinforced-concrete frame structures including beams and columns.""",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool, calc_tool]
)

verifier = Agent(
    llm=openai_llm,
    role='Structural Engineer Verifier',
    goal="""Verify and check whether the numbers given to you are correct.""",
    backstory="""You are a renowned structural engineering verifier and reviewer.
    You are very good at spotting errors in mistakes in calculations given to you.""",
    verbose=True,
    allow_delegation=True,
    tools=[search_tool, calc_tool]
)

# Create tasks for your agents
design = Task(
    description=f"""Do the calculation for a reinforced-concrete beam design following the 
    American Concrete Institute, ACI 318, design standard for the following case:
    "{problem}". Your input to the calculator tool should be integer or float in the following
    order otherwise it will not work: beam width, beam depth or height, concrete compressive strength, 
    steel yield strength, bending moment and shear force.
    Your final answer should be the amount of reinforcement for flexure and shear in square-millimeters.
    You can use the search tool for the required formula.""",
    agent=engineer
)

verify = Task(
    description="""fDo the calculation for a reinforced-concrete beam design following the 
    American Concrete Institute, ACI 318, design standard for the following case:
    "{problem}".Your input to the calculator tool should be integer or float in the following
    order otherwise it will not work: beam width, beam depth or height, concrete compressive strength, 
    steel yield strength, bending moment and shear force.
    Your final answer should be the amount of reinforcement for flexure and shear in square-millimeters.
    You can use the search tool for the required formula. Finally, compare your answers with those that
    were given to you and decide whether they are correct or not. State your reasoning and show your
    calculations but note that within 2 percent is considered valid.""",
    agent=verifier
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[engineer, verifier],
    tasks=[design, verify],
    process=Process.sequential,
    verbose=2,  # You can set it to 1 or 2 to different logging levels
)

# Get your crew to work!DD
result = crew.kickoff()

print("######################")
print(result)

with open('./beam-results.txt', 'w+') as f:
    f.write('########################')
    f.write(result)
    f.write('########################')
