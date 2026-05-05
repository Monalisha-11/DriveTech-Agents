#!/usr/bin/env python3
"""
DriveTech-Agents: Comprehensive Azure-Native Architecture Diagram Generator
=============================================================================
Generates a single, complete PNG architecture diagram with:
  - Network segmentation (VNet, subnets, NSGs, private endpoints)
  - Resource specifications (SKUs, tiers, instance counts)
  - Ports & protocols on every connection
  - Azure-native icon representations (via mingrammer/diagrams)

Usage:
    pip install diagrams          # requires graphviz system package
    python generate_architecture_diagram.py

Output:
    drivetech_azure_architecture.png   (in the current working directory)
"""

from diagrams import Cluster, Diagram, Edge

# ── Azure-native icon imports ──────────────────────────────────────────────
from diagrams.azure.network import (
    ApplicationGateway,
    Firewall,
    FrontDoors,
    LoadBalancers,
    NetworkSecurityGroupsClassic as NSG,
    PrivateEndpoint,
    Subnets,
    VirtualNetworks,
    DNSPrivateZones,
    TrafficManagerProfiles,
    VirtualNetworkGateways,
)
from diagrams.azure.compute import (
    AKS,
    AppServices,
    ContainerApps,
    ContainerRegistries,
    FunctionApps,
    VM,
    VMSS,
)
from diagrams.azure.database import (
    CacheForRedis,
    CosmosDb,
    SQLDatabases,
    SQLServers,
)
from diagrams.azure.web import (
    APIManagementServices,
    AppServicePlans,
    CognitiveServices,
    StaticApps,
)
from diagrams.azure.security import KeyVaults, Defender
from diagrams.azure.integration import (
    AzureServiceBus as ServiceBus,
    EventGridTopics,
    LogicApps,
)
from diagrams.azure.storage import BlobStorage, QueuesStorage, StorageAccounts
from diagrams.azure.identity import ActiveDirectory, ManagedIdentities, Users
from diagrams.azure.general import Helpsupport
from diagrams.generic.device import Mobile, Tablet
from diagrams.onprem.client import Client


# ── Colour palette for edges (by traffic type) ────────────────────────────
HTTPS   = "darkgreen"
GRPC    = "royalblue"
AMQP    = "darkorange"
SQL_CLR = "firebrick"
REDIS   = "crimson"
PRIV    = "gray"
MGMT    = "slategray"


def generate_diagram(output_filename: str = "drivetech_azure_architecture") -> str:
    """
    Build and render the full DriveTech Azure architecture diagram.

    Parameters
    ----------
    output_filename : str
        Base name for the output file (without extension).
        The library appends '.png' automatically.

    Returns
    -------
    str
        The path of the generated PNG file.
    """

    graph_attr = {
        "fontsize": "11",
        "fontname": "Segoe UI",
        "bgcolor": "white",
        "pad": "0.8",
        "nodesep": "0.8",
        "ranksep": "1.2",
        "splines": "ortho",
        "label": (
            "DriveTech-Agents  ·  Azure-Native Architecture\n"
            "────────────────────────────────────────────────────────────\n"
            "Region: East US (Primary)  |  West US (DR/Failover)\n"
            "Legend:  Green = HTTPS/443  |  Blue = gRPC/443  |  "
            "Orange = AMQP/5671  |  Red = SQL/1433  |  Gray = Private Link"
        ),
        "labelloc": "t",
        "labeljust": "c",
    }

    with Diagram(
        "",
        filename=output_filename,
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=graph_attr,
    ):

        # ─── External Callers ─────────────────────────────────────────
        with Cluster("External Callers"):
            browser  = Client("Browser\nClients")
            mobile   = Mobile("Mobile Apps\n(iOS / Android)")
            partner  = Client("Partner APIs\n(B2B / OEM)")

        # ─── Azure AD / Entra ID ──────────────────────────────────────
        with Cluster("Identity & Access (Entra ID)\nTenant: drivetech.onmicrosoft.com"):
            aad      = ActiveDirectory("Azure AD\nOAuth 2.0 / OIDC")
            msi      = ManagedIdentities("Managed\nIdentities")

        # ─── Edge / Ingress ───────────────────────────────────────────
        with Cluster("Edge Network"):
            frontdoor = FrontDoors(
                "Azure Front Door\nPremium SKU\nWAF Policy: OWASP 3.2\n"
                "Custom Domain: api.drivetech.io\nTLS 1.3 · HTTP→HTTPS redirect"
            )
            tm = TrafficManagerProfiles(
                "Traffic Manager\nPriority routing\n"
                "East US → West US failover"
            )

        # ─── Primary Region ──────────────────────────────────────────
        with Cluster(
            "Primary Region – East US\n"
            "VNet: drivetech-vnet-eastus  10.0.0.0/16"
        ):
            # ── App Gateway Subnet ────────────────────────────────────
            with Cluster(
                "Subnet: snet-appgw  10.0.0.0/24\n"
                "NSG: nsg-appgw  ·  Allow 443 inbound from Front Door"
            ):
                appgw = ApplicationGateway(
                    "App Gateway v2\nWAF_v2 SKU\n"
                    "Listener: 443/HTTPS\nBackend: AKS Ingress\n"
                    "Health probe: /healthz\nAutoscale: 2-10"
                )
                nsg_appgw = NSG("NSG: nsg-appgw\nInbound 443 from\nFrontDoor.Backend\nDeny all other")

            # ── AKS Subnet ────────────────────────────────────────────
            with Cluster(
                "Subnet: snet-aks  10.0.4.0/22\n"
                "NSG: nsg-aks  ·  Allow 443 from snet-appgw"
            ):
                nsg_aks = NSG(
                    "NSG: nsg-aks\n"
                    "Inbound 443 from 10.0.0.0/24\n"
                    "Inbound 9090 (Prometheus)\n"
                    "Outbound 443 to Internet\n"
                    "Outbound 1433 to snet-data"
                )
                aks = AKS(
                    "AKS Cluster\ndrivetech-aks-eastus\n"
                    "K8s 1.29 · Standard_D4s_v5\n"
                    "System pool: 3 nodes\n"
                    "User pool: 3-10 nodes (autoscale)\n"
                    "CNI: Azure CNI Overlay\n"
                    "Ingress: NGINX 443/HTTPS"
                )
                acr = ContainerRegistries(
                    "ACR\ndrivetechacr.azurecr.io\n"
                    "Premium SKU\nGeo-replicated"
                )

            # ── Microservices inside AKS ──────────────────────────────
            with Cluster(
                "AKS Workloads (Namespaces)\n"
                "Service Mesh: Istio  ·  mTLS enforced"
            ):
                api_gw     = AppServices("API Gateway\nService\nPort 8080/HTTP")
                vehicle_svc = ContainerApps(
                    "Vehicle Agent\nService\nPort 8081/gRPC"
                )
                driver_svc  = ContainerApps(
                    "Driver Agent\nService\nPort 8082/gRPC"
                )
                trip_svc    = ContainerApps(
                    "Trip Orchestrator\nService\nPort 8083/gRPC"
                )
                telemetry_svc = ContainerApps(
                    "Telemetry\nIngestion Service\nPort 8084/gRPC"
                )
                ai_svc      = ContainerApps(
                    "AI/ML Agent\nService\nPort 8085/HTTP"
                )
                notif_svc   = ContainerApps(
                    "Notification\nService\nPort 8086/HTTP"
                )

            # ── Functions Subnet ──────────────────────────────────────
            with Cluster(
                "Subnet: snet-functions  10.0.8.0/24\n"
                "NSG: nsg-func  ·  VNet-integrated"
            ):
                fn_trip     = FunctionApps(
                    "fn-trip-processor\n"
                    "Consumption Plan\n"
                    "Trigger: Service Bus\n"
                    "Runtime: .NET 8"
                )
                fn_telemetry = FunctionApps(
                    "fn-telemetry-agg\n"
                    "Premium EP1\n"
                    "Trigger: Event Grid\n"
                    "Runtime: Python 3.11"
                )
                fn_scheduler = FunctionApps(
                    "fn-scheduler\n"
                    "Consumption Plan\n"
                    "Trigger: Timer (cron)\n"
                    "Runtime: .NET 8"
                )

            # ── Integration Subnet ────────────────────────────────────
            with Cluster(
                "Subnet: snet-integration  10.0.10.0/24\n"
                "NSG: nsg-integration"
            ):
                sbus = ServiceBus(
                    "Service Bus\nPremium SKU · 1 MU\n"
                    "Namespace: drivetech-sb\n"
                    "Topics: trip-events,\n"
                    "vehicle-commands,\n"
                    "driver-notifications\n"
                    "Protocol: AMQP/5671 TLS"
                )
                evgrid = EventGridTopics(
                    "Event Grid\nTopic: telemetry-events\n"
                    "Schema: CloudEvents v1.0\n"
                    "Protocol: HTTPS/443"
                )
                logic = LogicApps(
                    "Logic App\n(Standard)\n"
                    "Workflow: OEM-Data-Sync\n"
                    "Triggers: HTTP webhook"
                )

            # ── Data Subnet ───────────────────────────────────────────
            with Cluster(
                "Subnet: snet-data  10.0.12.0/24\n"
                "NSG: nsg-data  ·  Allow 1433,6380,443 from\n"
                "snet-aks & snet-functions only"
            ):
                nsg_data = NSG(
                    "NSG: nsg-data\n"
                    "Inbound 1433 from 10.0.4.0/22\n"
                    "Inbound 6380 from 10.0.4.0/22\n"
                    "Inbound 443 from 10.0.8.0/24\n"
                    "Deny all other inbound"
                )
                sql = SQLServers(
                    "Azure SQL Server\ndrivetech-sql-eastus\n"
                    "Business Critical\nGen5 8 vCores\n"
                    "Port: 1433/TDS\n"
                    "TDE enabled · AAD auth"
                )
                sqldb_trip = SQLDatabases("DB: TripDB\n100 DTU")
                sqldb_vehicle = SQLDatabases("DB: VehicleDB\n100 DTU")
                sqldb_driver = SQLDatabases("DB: DriverDB\n50 DTU")
                cosmos = CosmosDb(
                    "Cosmos DB\n"
                    "API: NoSQL\n"
                    "drivetech-cosmos-eastus\n"
                    "Multi-region writes\n"
                    "Port: 443/HTTPS\n"
                    "Containers: telemetry,\n"
                    "agent-state, sessions"
                )
                redis = CacheForRedis(
                    "Azure Cache for Redis\n"
                    "Premium P1 · 6 GB\n"
                    "Port: 6380/TLS\n"
                    "Cluster mode enabled\n"
                    "Used for: session cache,\n"
                    "rate limiting, pub/sub"
                )

            # ── Private Endpoints ─────────────────────────────────────
            with Cluster(
                "Subnet: snet-privateendpoints  10.0.14.0/24\n"
                "Private DNS Zones integrated"
            ):
                pe_sql   = PrivateEndpoint("PE: SQL\n10.0.14.4\nprivatelink.\n"
                                           "database.windows.net")
                pe_cosmos = PrivateEndpoint("PE: Cosmos\n10.0.14.5\nprivatelink.\n"
                                            "documents.azure.com")
                pe_redis = PrivateEndpoint("PE: Redis\n10.0.14.6\nprivatelink.\n"
                                           "redis.cache.windows.net")
                pe_sb    = PrivateEndpoint("PE: Service Bus\n10.0.14.7\nprivatelink.\n"
                                           "servicebus.windows.net")
                pe_kv    = PrivateEndpoint("PE: Key Vault\n10.0.14.8\nprivatelink.\n"
                                           "vaultcore.azure.net")
                pe_acr   = PrivateEndpoint("PE: ACR\n10.0.14.9\nprivatelink.\n"
                                           "azurecr.io")
                dns = DNSPrivateZones("Private DNS Zones\n"
                                      "*.database.windows.net\n"
                                      "*.documents.azure.com\n"
                                      "*.redis.cache.windows.net\n"
                                      "*.servicebus.windows.net\n"
                                      "*.vaultcore.azure.net\n"
                                      "*.azurecr.io")

            # ── Security & Config ─────────────────────────────────────
            with Cluster("Security & Configuration"):
                kv = KeyVaults(
                    "Key Vault\ndrivetech-kv-eastus\n"
                    "Premium SKU · HSM\n"
                    "Secrets: DB conn strings,\n"
                    "API keys, certificates\n"
                    "Access: RBAC (MSI only)"
                )
                defender = Defender(
                    "Defender for Cloud\n"
                    "CSPM + CWP enabled\n"
                    "Container scanning"
                )

            # ── Storage ───────────────────────────────────────────────
            with Cluster(
                "Subnet: snet-storage  10.0.16.0/24\n"
                "Service Endpoints enabled"
            ):
                blob = BlobStorage(
                    "Blob Storage\ndrivetechsteastus\n"
                    "StorageV2 · LRS\n"
                    "Containers:\n"
                    "  vehicle-images\n"
                    "  trip-documents\n"
                    "  ml-models\n"
                    "Access: Private endpoint"
                )
                queue = QueuesStorage(
                    "Queue Storage\n"
                    "Dead-letter queue\n"
                    "backup"
                )

            # ── Monitoring ────────────────────────────────────────────
            with Cluster("Observability"):
                appinsights = Helpsupport(
                    "Application Insights\n"
                    "Log Analytics Workspace\n"
                    "drivetech-law-eastus\n"
                    "Retention: 90 days\n"
                    "Sampling: Adaptive"
                )

        # ── External / 3rd-Party Services ─────────────────────────────
        with Cluster("External / 3rd-Party Services"):
            maps_api   = CognitiveServices("Azure Maps API\nRouting & Geocoding\nHTTPS/443")
            openai_api = CognitiveServices("Azure OpenAI\nGPT-4o · Embeddings\nHTTPS/443")
            sms_gw     = Client("Twilio / SendGrid\nSMS & Email\nHTTPS/443")
            oem_api    = Client("OEM Telematics\nAPIs (3rd party)\nHTTPS/443")

        # ──────────────────────────────────────────────────────────────
        #  CONNECTIONS  –  every arrow annotated with protocol & port
        # ──────────────────────────────────────────────────────────────

        # External → Edge
        browser  >> Edge(label="HTTPS/443\nTLS 1.3", color=HTTPS) >> frontdoor
        mobile   >> Edge(label="HTTPS/443\nTLS 1.3", color=HTTPS) >> frontdoor
        partner  >> Edge(label="HTTPS/443\nmTLS", color=HTTPS) >> frontdoor

        # Auth
        browser  >> Edge(label="OAuth 2.0\nHTTPS/443", color=HTTPS, style="dashed") >> aad
        mobile   >> Edge(label="OIDC\nHTTPS/443", color=HTTPS, style="dashed") >> aad

        # Edge → App Gateway
        frontdoor >> Edge(label="HTTPS/443\nX-Azure-FDID header", color=HTTPS) >> appgw

        # App Gateway → AKS
        appgw >> Edge(label="HTTPS/443\nSNI routing", color=HTTPS) >> aks

        # AKS Ingress → Microservices
        aks >> Edge(label="HTTP/8080", color=HTTPS) >> api_gw
        api_gw >> Edge(label="gRPC/8081\nProtobuf", color=GRPC) >> vehicle_svc
        api_gw >> Edge(label="gRPC/8082\nProtobuf", color=GRPC) >> driver_svc
        api_gw >> Edge(label="gRPC/8083\nProtobuf", color=GRPC) >> trip_svc
        api_gw >> Edge(label="gRPC/8084\nProtobuf", color=GRPC) >> telemetry_svc
        api_gw >> Edge(label="HTTP/8085\nREST/JSON", color=HTTPS) >> ai_svc
        api_gw >> Edge(label="HTTP/8086\nREST/JSON", color=HTTPS) >> notif_svc

        # Services → Data (via Private Endpoints)
        trip_svc      >> Edge(label="TDS/1433\nEncrypted", color=SQL_CLR) >> pe_sql
        vehicle_svc   >> Edge(label="TDS/1433\nEncrypted", color=SQL_CLR) >> pe_sql
        driver_svc    >> Edge(label="TDS/1433\nEncrypted", color=SQL_CLR) >> pe_sql
        telemetry_svc >> Edge(label="HTTPS/443\nDirect mode", color=HTTPS) >> pe_cosmos
        ai_svc        >> Edge(label="HTTPS/443", color=HTTPS) >> pe_cosmos
        api_gw        >> Edge(label="TLS/6380", color=REDIS) >> pe_redis

        # Private Endpoints → Data Resources
        pe_sql    >> Edge(label="Private Link", color=PRIV, style="dotted") >> sql
        pe_cosmos >> Edge(label="Private Link", color=PRIV, style="dotted") >> cosmos
        pe_redis  >> Edge(label="Private Link", color=PRIV, style="dotted") >> redis
        pe_sb     >> Edge(label="Private Link", color=PRIV, style="dotted") >> sbus
        pe_kv     >> Edge(label="Private Link", color=PRIV, style="dotted") >> kv
        pe_acr    >> Edge(label="Private Link", color=PRIV, style="dotted") >> acr

        # SQL Server → Databases
        sql >> Edge(color=SQL_CLR, style="dotted") >> sqldb_trip
        sql >> Edge(color=SQL_CLR, style="dotted") >> sqldb_vehicle
        sql >> Edge(color=SQL_CLR, style="dotted") >> sqldb_driver

        # Services → Service Bus (via PE)
        trip_svc    >> Edge(label="AMQP/5671\nTLS", color=AMQP) >> pe_sb
        vehicle_svc >> Edge(label="AMQP/5671\nTLS", color=AMQP) >> pe_sb
        notif_svc   >> Edge(label="AMQP/5671\nTLS", color=AMQP) >> pe_sb

        # Service Bus → Functions
        sbus >> Edge(label="AMQP/5671\nTrigger", color=AMQP) >> fn_trip
        sbus >> Edge(label="AMQP/5671\nTrigger", color=AMQP) >> fn_scheduler

        # Event Grid → Functions
        telemetry_svc >> Edge(label="HTTPS/443\nCloudEvents", color=HTTPS) >> evgrid
        evgrid >> Edge(label="HTTPS/443\nPush", color=HTTPS) >> fn_telemetry

        # Functions → Data
        fn_trip      >> Edge(label="TDS/1433", color=SQL_CLR) >> pe_sql
        fn_telemetry >> Edge(label="HTTPS/443", color=HTTPS) >> pe_cosmos
        fn_scheduler >> Edge(label="AMQP/5671", color=AMQP) >> pe_sb

        # Logic App → External
        logic >> Edge(label="HTTPS/443\nWebhook", color=HTTPS) >> oem_api

        # Services → Key Vault (secrets)
        aks >> Edge(label="HTTPS/443\nMSI auth", color=MGMT, style="dashed") >> pe_kv

        # Services → External APIs
        ai_svc        >> Edge(label="HTTPS/443", color=HTTPS) >> openai_api
        trip_svc      >> Edge(label="HTTPS/443", color=HTTPS) >> maps_api
        notif_svc     >> Edge(label="HTTPS/443", color=HTTPS) >> sms_gw
        vehicle_svc   >> Edge(label="HTTPS/443", color=HTTPS) >> oem_api

        # Services → Blob Storage
        vehicle_svc >> Edge(label="HTTPS/443\nBlob REST", color=HTTPS) >> blob
        ai_svc      >> Edge(label="HTTPS/443\nBlob REST", color=HTTPS) >> blob

        # AKS → ACR (image pull)
        aks >> Edge(label="HTTPS/443\nDocker pull\nMSI auth", color=MGMT, style="dashed") >> pe_acr

        # Monitoring
        aks          >> Edge(label="HTTPS/443\nOTel", color=MGMT, style="dashed") >> appinsights
        fn_trip      >> Edge(label="HTTPS/443", color=MGMT, style="dashed") >> appinsights
        fn_telemetry >> Edge(label="HTTPS/443", color=MGMT, style="dashed") >> appinsights

        # DNS
        pe_sql   >> Edge(color=PRIV, style="dotted") >> dns
        pe_cosmos >> Edge(color=PRIV, style="dotted") >> dns
        pe_redis >> Edge(color=PRIV, style="dotted") >> dns
        pe_sb    >> Edge(color=PRIV, style="dotted") >> dns
        pe_kv    >> Edge(color=PRIV, style="dotted") >> dns
        pe_acr   >> Edge(color=PRIV, style="dotted") >> dns

        # MSI
        aks     >> Edge(label="MSI", color=MGMT, style="dashed") >> msi
        fn_trip >> Edge(label="MSI", color=MGMT, style="dashed") >> msi

    output_path = f"{output_filename}.png"
    return output_path


# ── PNG Export Helper ─────────────────────────────────────────────────────
def export_png(output_path: str = "drivetech_azure_architecture") -> str:
    """
    Public export function that generates the architecture diagram as PNG.

    Parameters
    ----------
    output_path : str, optional
        Base filename (no extension). Defaults to
        ``drivetech_azure_architecture``.

    Returns
    -------
    str
        Absolute or relative path to the generated ``.png`` file.

    Example
    -------
    >>> from generate_architecture_diagram import export_png
    >>> png_file = export_png()
    >>> print(f"Diagram saved to {png_file}")
    """
    import os

    result = generate_diagram(output_filename=output_path)
    abs_path = os.path.abspath(result)
    print(f"✅  Architecture diagram exported: {abs_path}")
    print(f"    Size: {os.path.getsize(abs_path):,} bytes")
    return abs_path


# ── CLI entry-point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    export_png()
