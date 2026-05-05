# DriveTech-Agents

Creating Agents for DriveTech Applications

## Azure Architecture Diagram

A comprehensive Azure-native architecture diagram for the DriveTech platform, rendered as a high-resolution PNG with:

- **Network segmentation** – VNet `10.0.0.0/16`, 7 purpose-built subnets with dedicated NSGs
- **Resource specifications** – SKUs, tiers, instance counts, autoscale ranges
- **Ports & protocols** – Every connection annotated (HTTPS/443, gRPC/8081-8086, AMQP/5671, TDS/1433, TLS/6380)
- **Azure-native icons** – Official Azure service icons via the `diagrams` library
- **Private Link / Private Endpoints** – All data-plane traffic stays on the VNet
- **Edge security** – Front Door Premium with WAF (OWASP 3.2), App Gateway v2

### Quick Start

```bash
# Prerequisites
pip install diagrams        # Python >= 3.9
sudo apt-get install graphviz   # or brew install graphviz on macOS

# Generate the diagram
python generate_architecture_diagram.py
```

### Programmatic PNG Export

```python
from generate_architecture_diagram import export_png

png_path = export_png()                          # default filename
png_path = export_png("my_custom_filename")      # custom filename
```

### Architecture Components

| Layer | Azure Service | Subnet | Key Ports |
|-------|--------------|--------|-----------|
| Edge | Front Door Premium + WAF | — | 443/HTTPS |
| Ingress | Application Gateway v2 (WAF_v2) | `snet-appgw 10.0.0.0/24` | 443/HTTPS |
| Compute | AKS (Standard_D4s_v5, 3-10 nodes) | `snet-aks 10.0.4.0/22` | 443, 8080-8086 |
| Serverless | Azure Functions (.NET 8, Python 3.11) | `snet-functions 10.0.8.0/24` | Triggered |
| Messaging | Service Bus Premium, Event Grid | `snet-integration 10.0.10.0/24` | 5671/AMQP |
| Data | Azure SQL (Business Critical), Cosmos DB, Redis P1 | `snet-data 10.0.12.0/24` | 1433, 443, 6380 |
| Private Link | 6 Private Endpoints + DNS Zones | `snet-privateendpoints 10.0.14.0/24` | — |
| Storage | Blob Storage (LRS) | `snet-storage 10.0.16.0/24` | 443/HTTPS |
| Security | Key Vault (Premium HSM), Defender for Cloud | — | 443/HTTPS |
| Identity | Entra ID (OAuth 2.0 / OIDC), Managed Identities | — | 443/HTTPS |

### Generated Output

The pre-generated diagram is available at [`drivetech_azure_architecture.png`](drivetech_azure_architecture.png).
