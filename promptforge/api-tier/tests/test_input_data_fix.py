import pytest
from httpx import AsyncClient
from sqlalchemy import text

@pytest.mark.asyncio
async def test_system_prompt_in_input_data(client: AsyncClient, auth_headers: dict, demo_user, db_session):
    """Verify system_prompt is stored in input_data for UI access"""
    
    # Create an insight with custom system prompts (transcript must be >= 100 chars)
    response = await client.post(
        "/api/v1/call-insights/analyze",
        headers=auth_headers,
        json={
            "transcript": "Customer: Hi, I need help with my order. Agent: Of course! What's your order number? Customer: It's 12345. Agent: Let me check... Your order is being processed and will ship tomorrow. Customer: Great, thank you!",
            "transcript_title": "DB Input Data Test",
            "system_prompts": {
                "stage1_fact_extraction": "DBTEST: Fact extractor",
                "stage2_reasoning": "DBTEST: Reasoner",
                "stage3_summary": "DBTEST: Summarizer"
            }
        }
    )
    
    assert response.status_code == 200, f"Got {response.status_code}: {response.json()}"
    data = response.json()
    trace_id = data["traces"][0]["trace_id"]
    
    print(f"\n=== Created trace: {trace_id} ===")
    
    # Query database directly for this trace
    result = await db_session.execute(
        text("SELECT input_data, trace_metadata FROM traces WHERE trace_id = :trace_id"),
        {"trace_id": trace_id}
    )
    row = result.fetchone()
    
    assert row is not None, f"Trace {trace_id} not found in database"
    input_data, trace_metadata = row
    
    print(f"\n=== Input Data ===")
    print(f"Keys: {list(input_data.keys())}")
    print(f"system_prompt: {input_data.get('system_prompt')}")
    
    print(f"\n=== Trace Metadata ===")
    print(f"system_prompt (first 100 chars): {str(trace_metadata.get('system_prompt', ''))[:100]}")
    
    # Verify system_prompt is in input_data
    assert "system_prompt" in input_data, "system_prompt not in input_data"
    assert input_data["system_prompt"] == "DBTEST: Fact extractor", \
        f"Expected 'DBTEST: Fact extractor', got '{input_data.get('system_prompt')}'"
    
    print("\n✅ SUCCESS: system_prompt correctly stored in input_data")
