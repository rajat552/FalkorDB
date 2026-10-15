"""
Ingest enterprise documents into FalkorDB.
Run with: python ingest.py
Or force fresh re-indexing: python ingest.py --force
"""
import sys
from app.db import check_health, init_schema
from app.ingestion.pipeline import ingest_enterprise_dataset

def main():
    force = "--force" in sys.argv or "-f" in sys.argv

    print("Checking FalkorDB connection...")
    health = check_health()
    if not health.get("connected"):
        print(f"Error: Could not connect to FalkorDB at {health.get('host')}:{health.get('port')}")
        print(f"Details: {health.get('error')}")
        print("Please ensure your Docker container is running: docker ps")
        sys.exit(1)

    print("Connected to FalkorDB successfully!")
    print("Initializing schema indexes...")
    init_schema()

    if force:
        print("Purging existing synthetic dataset nodes for fresh ingestion (--force)...")
    else:
        print("Ingesting enterprise documents into graph (deduplicating unchanged files)...")

    summary = ingest_enterprise_dataset(force=force)
    ingested_count = len(summary.get("ingested", []))
    skipped_count = len(summary.get("skipped", []))
    total_active = summary.get("total_active", 0)

    print(f"Ingestion complete! {ingested_count} newly indexed, {skipped_count} skipped duplicates.")
    print(f"Total active documents in FalkorDB: {total_active}")

    final_health = check_health()
    print(f"Graph summary: {final_health.get('total_nodes')} nodes, {final_health.get('total_edges')} edges.")

if __name__ == "__main__":
    main()
