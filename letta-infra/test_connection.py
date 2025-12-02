from letta_client import Letta

try:
    client = Letta(base_url="http://localhost:8283")
    
    # Test connection by listing agents
    agents = list(client.agents.list())
    print("[OK] SDK connected successfully")
    print(f"  Found {len(agents)} existing agents")
    
except Exception as e:
    print(f"[FAIL] SDK connection failed: {e}")
