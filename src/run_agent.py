from src.agent.azure_llm import AzureLLM
from src.agent.toolbox import ToolBox, TOOL_SCHEMAS
from src.agent.loop import run_agent
from src.agent.proposal import build_proposal

llm = AzureLLM()
box = ToolBox()

run_agent(llm, box, "Check my Azure subscription for wasted spend.", TOOL_SCHEMAS)
proposal = build_proposal(box.findings, llm)

print(proposal.summary, "\n")
for f in proposal.findings:
    print(f"[{f.risk.upper()}] {f.resource_name}: ~${f.est_monthly_cost_usd}/month")
print(f"\nTotal: ~${proposal.total_monthly_savings_usd}/month "
      f"(approval required: {proposal.requires_approval})")