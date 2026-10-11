import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest

load_dotenv()

SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]


def run_query(query: str) -> list[dict]:
    """Run a Resource Graph (KQL) query and return rows as dicts."""
    client = ResourceGraphClient(DefaultAzureCredential())
    request = QueryRequest(subscriptions=[SUBSCRIPTION_ID], query=query)
    response = client.resources(request)
    return response.data


def list_resources() -> list[dict]:
    return run_query(
        "Resources | project name, type, resourceGroup, location, tags"
    )


def find_unattached_disks() -> list[dict]:
    return run_query(
        """
        Resources
        | where type =~ 'microsoft.compute/disks'
        | where isempty(managedBy)
        | project name, resourceGroup, sizeGb = properties.diskSizeGB,
                  sku = sku.name, tags
        """
    )

def find_unattached_public_ips() -> list[dict]:
    return run_query(
        """
        Resources
        | where type =~ 'microsoft.network/publicipaddresses'
        | where isnull(properties.ipConfiguration)
              and isnull(properties.natGateway)
        | project name, resourceGroup, sku = sku.name,
                  allocation = properties.publicIPAllocationMethod, tags
        """
    )


if __name__ == "__main__":
    print("All resources:")
    for r in list_resources():
        print(" ", r["name"], "|", r["type"], "|", r["resourceGroup"])

    print("\nUnattached disks:")
    for d in find_unattached_disks():
        print(" ", d)

    print("\nUnattached public IPs:")
    for ip in find_unattached_public_ips():
        print(" ", ip)