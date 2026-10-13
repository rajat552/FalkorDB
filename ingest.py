"""
Ingest enterprise documents into FalkorDB.
Run with: python ingest.py
"""
import sys
from app.db import check_health, init_schema
from app.ingestion.pipeline import ingest_enterprise_dataset

def main():
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

    print("Ingesting enterprise documents into graph...")
    results = ingest_enterprise_dataset()
    print(f"Ingestion complete! Successfully processed {len(results)} files.")

    final_health = check_health()
    print(f"Graph summary: {final_health.get('total_nodes')} nodes, {final_health.get('total_edges')} edges.")

if __name__ == "__main__":
    main()
