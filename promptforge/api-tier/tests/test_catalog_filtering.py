"""
Test evaluation catalog filtering with registered adapters
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_catalog_returns_evaluations(
    client: AsyncClient,
    auth_headers: dict,
    demo_user: User,
    db_session: AsyncSession,
):
    """
    Test that catalog endpoint returns evaluations with registered adapters
    GIVEN: Registered adapters in the system
    WHEN: GET /api/v1/evaluation-catalog/catalog
    THEN: Returns evaluations whose adapters are registered
    """
    # Get catalog
    response = await client.get(
        "/api/v1/evaluation-catalog/catalog?is_active=true",
        headers=auth_headers,
    )

    assert response.status_code == 200
    evaluations = response.json()

    # Should return evaluations
    assert isinstance(evaluations, list)
    assert len(evaluations) > 0

    print(f"\n=== Catalog Response ===")
    print(f"Total evaluations returned: {len(evaluations)}")

    # Group by source
    by_source = {}
    for eval in evaluations:
        source = eval["source"]
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(eval)

    for source, evals in by_source.items():
        print(f"{source}: {len(evals)} evaluations")

    # Verify all evaluations have required fields
    for eval in evaluations:
        assert "id" in eval
        assert "name" in eval
        assert "source" in eval
        assert "category" in eval
        assert "evaluation_type" in eval

    # Check that PromptForge evaluations are included
    promptforge_evals = [e for e in evaluations if e["source"] == "PROMPTFORGE"]
    assert len(promptforge_evals) > 0, "Should include PromptForge evaluations"

    # Print sample
    if promptforge_evals:
        print(f"\nSample PromptForge evaluation: {promptforge_evals[0]['name']}")

    # Check that vendor evaluations are included
    vendor_evals = [e for e in evaluations if e["source"] == "VENDOR"]
    assert len(vendor_evals) > 0, "Should include vendor evaluations"

    if vendor_evals:
        print(f"Sample vendor evaluation: {vendor_evals[0]['name']}")

    print("======================\n")
