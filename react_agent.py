# # react_agent.py
# from langchain_core.prompts import PromptTemplate
# from langchain.agents import initialize_agent, Tool
# # from langchain.llms.ollama import Ollama

# from langchain_community.llms import Ollama

# from tools import call_api
# from vectorstore import retrieve_relevant_sop

# llm = Ollama(model="llama3.2",
#              num_ctx=4096,
#              temperature=0,
#              verbose=True)

# # tools = [
# #     Tool(
# #         name="APICaller",
# #         func=call_api,
# #         description="Call the correct API using the extracted parameters. Input is a JSON with 'endpoint', 'method', 'payload'."
# #     ),
# #     Tool(
# #         name="SOPRetriever",
# #         func=retrieve_relevant_sop,
# #         description="Given a case description, retrieve relevant SOP steps."
# #     )
# # ]

# # agent = initialize_agent(
# #     tools,
# #     llm,
# #     agent="zero-shot-react-description",
# #     verbose=True
# # )

# # def resolve_ticket(case_description: str):
# #     print("\nAgent Starting...")
# #     agent.run(f"Resolve this ticket:\n{case_description}")


# # agent.py
# from langchain.llms import Ollama
# from langchain.agents import initialize_agent, AgentType, Tool
# from langchain_community.llms import Ollama

# from tools import call_api
# from vectorstore import retrieve_relevant_sop

# # llm = Ollama(model="llama3:instruct")


# llm = Ollama(model="llama3.2",
#              num_ctx=4096,
#              temperature=0,
#              verbose=True)

# def resolve_ticket_with_agent(ticket_text: str):
#     # STEP 1: Retrieve SOPs from vector DB
#     sop_context = retrieve_relevant_sop(ticket_text)
#     print("\n\nsop fetched from DB: ", sop_context)
#     # STEP 2: Define tools (API caller)
#     tools = [
#         Tool(
#             name="APICaller",
#             func=call_api,
#             description="Use this to call the correct API. Input must include 'endpoint', 'method', and 'payload'."
#         )
#     ]

#     # STEP 3: Add the SOP context to the agent prompt
#     prompt_prefix = f"""You are a backend engineer assistant that helps resolve tickets by interpreting them and following SOPs.

# Here are the relevant SOPs retrieved for this ticket:
# {sop_context}

# You must determine the correct API to call and prepare the correct payload.

# When you're ready, use the APICaller tool to perform the action.

# """

#     agent = initialize_agent(
#         tools,
#         llm,
#         agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#         verbose=True,
#         agent_kwargs={
#             "prefix": prompt_prefix
#         }
#     )

#     return agent.run(ticket_text)


# agent.py
from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, AgentType, Tool
from tools import call_api
from vectorstore import retrieve_relevant_sop

llm = Ollama(
    model="llama3.2",
    num_ctx=4096,
    temperature=0,
    verbose=True
)

def resolve_ticket_with_agent(ticket_text: str):
    sop_context = retrieve_relevant_sop(ticket_text)
    print("\n\nsop fetched from DB: ", sop_context)

    tools = [
        Tool(
            name="APICaller",
            func=call_api,
            description="Use this to call an API. Input format: {\"endpoint\": ..., \"method\": ..., \"payload\": {...}}"
        )
    ]

    prompt_prefix = f"""
You are an agent that resolves merchant support tickets using APIs. 
You are provided with a ticket and relevant SOPs.
First think through what is needed, then use the APICaller tool ONCE to call the required API.
Do NOT retry the same call if it fails. Just report the failure and stop.

--- SOPs START ---
{sop_context}
--- SOPs END ---

Think step-by-step.
If the API call succeeds, output the result and stop.
"""

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"prefix": prompt_prefix},
        max_iterations=3
    )

    return agent.run(ticket_text)
