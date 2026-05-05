---
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

name: Architecture Diagrams
description: Create/Generate Azure Native Architecture Diagrams
---

# My Agent

  “Scan the solution and identify:
All executable entry points (web apps, APIs, functions, workers, services, console apps). The main request entry (UI/API gateway/controller endpoints) and background entry points (queues, schedulers). External dependencies referenced in code (databases, queues, storage, third-party APIs). Return: A) A concise component list B) A ‘where to look’ file list (top files/projects for each component). If you are unsure, show the evidence (file paths / project names) you used.”

  “Create an end-to-end application flow narrative:
Start from the external caller (browser/mobile/partner system) → all internal hops → persistence → downstream integrations → response. Include async flows (queues/events/cron jobs) separately. Output:
‘Happy path’ flow (numbered steps) ‘Async/event’ flow (numbered steps) Key data stores and what they store (high level). Cite the code artefacts (projects/files/classes) that support each hop.”

  “Inventory all endpoints:
Public HTTP endpoints (routes/controllers/minimal APIs) Internal service endpoints (gRPC, internal HTTP) Messaging endpoints (Service Bus queues/topics, RabbitMQ, etc.) DB endpoints (SQL, Cosmos, etc.) Return a table: Endpoint | Type | Auth mechanism | Caller | Target | Notes | Evidence (file/class). If ports aren’t explicit, mark as ‘Not evidenced’.”

  “Search the repo for infrastructure & deployment evidence:
IaC (bicep, arm, terraform), dockerfiles, k8s manifests, helm charts Azure DevOps/GitHub pipelines and deployment scripts app configuration (appsettings*.json, env var keys, Key Vault refs) Return:
List of infra-related files found (with paths) What Azure resources are explicitly defined Any networking constructs found (VNet/subnet/NSG/private endpoint/app gateway/front door) If none exist, say ‘No infra evidence found in repo’.”

  “Based on evidence found (and only then assumptions), propose an Azure-native target architecture mapping:
For each component, choose the most likely Azure service (App Service, AKS, Functions, VMSS/VM, SQL, Storage, Service Bus, Key Vault, Front Door/App Gateway, etc.) Clearly separate: ‘Evidenced in repo’ vs ‘Assumption’. Output a table: Component | Runtime | Azure service | Region notes (if any) | HA/DR approach | Evidence/Assumption.

“Now generate an Azure-native Icons architecture diagram in Mermaid (ADO Wiki compatible) with:
Network segmentation: VNet, subnets, NSGs, private endpoints (only if evidenced; else label as Assumption) Edge: Front Door/App Gateway/WAF (if evidenced or clearly marked) Compute: App Services/AKS/Functions/VMs (include VMs only if evidenced; else mark) Data: SQL/Cosmos/Storage Integration: Service Bus/Event Grid/Logic Apps (as applicable) External systems: third-party APIs Also include a small legend and clearly mark public vs private endpoints. Return ONLY:
A Mermaid ‘flowchart’ diagram (preferred LR) A second Mermaid diagram: ‘sequenceDiagram’ for one key business journey.”

“Create a second Mermaid diagram focused purely on network + endpoints:
Show ingress/egress paths Show DNS boundaries if relevant Show private link/private endpoints and subnet placement if evidenced Show VM NICs / load balancers / jumpbox patterns if evidenced Output as Mermaid flowchart with subgraphs: Edge, VNet, Subnets, Compute, Data, External. Where details are missing, list what repo evidence would be needed to confirm.”

“Validation pass:
For each component and each arrow in the diagram, list the evidence (file/config/IaC). Identify any arrows that are assumptions and propose how to confirm them (what file or config to check). Then regenerate the Mermaid flowchart with assumptions explicitly labelled.”


