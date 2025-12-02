from letta_client import Letta

client = Letta(base_url="http://localhost:8283")

# Create a test agent
agent = client.agents.create(
    model="openai/gpt-4o-mini",
    embedding="openai/text-embedding-3-small",
    memory_blocks=[
        {"label": "persona", "value": "I am a test agent."}
    ]
)

print(f"[OK] Agent created: {agent.id}")

# Send test message
response = client.agents.messages.create(
    agent_id=agent.id,
    messages=[{"role": "user", "content": "Hello, can you hear me?"}]
)

print(f"[OK] Agent responded with {len(response.messages)} messages")

# Cleanup
client.agents.delete(agent.id)
print("[OK] Test agent deleted")
