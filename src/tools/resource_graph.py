import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest, QueryRequestOptions

load_dotenv()

PAGE_SIZE = 1000   # Resource Graph maximum per call (the default is only 100)
MAX_PAGES = 100    # safety stop so a bug can never loop forever


def _subscription_id() -> str:
    return os.environ["AZURE_SUBSCRIPTION_ID"]


def _make_client() -> ResourceGraphClient:
    return ResourceGraphClient(DefaultAzureCredential())


def run_query(query: str) -> list[dict]:
    """Run a Resource Graph (KQL) query and return ALL rows, page by page."""
    client = _make_client()
    rows: list[dict] = []
    skip_token = None
    for _ in range(MAX_PAGES):
        options = QueryRequestOptions(top=PAGE_SIZE, skip_token=skip_token)
        request = QueryRequest(
            subscriptions=[_subscription_id()], query=query, options=options
        )
        response = client.resources(request)
        rows.extend(response.data)
        skip_token = response.skip_token
        if not skip_token:
            return rows
    raise RuntimeError("Resource Graph returned too many pages; stopping.")

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
        | project id, name, resourceGroup, location, managedBy, 
                diskState = properties.diskState,
                sizeGb = properties.diskSizeGB, sku = sku.name, tags
        """
    )

def find_unattached_public_ips() -> list[dict]:
    return run_query(
        """
        Resources
        | where type =~ 'microsoft.network/publicipaddresses'
        | where isnull(properties.ipConfiguration)
              and isnull(properties.natGateway)
        | project id, name, location, resourceGroup, sku = sku.name, skuTier = sku.tier,
                  allocation = properties.publicIPAllocationMethod, ipVersion = properties.publicIPAddressVersion, tags
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