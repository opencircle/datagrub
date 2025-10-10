"""
Test parent-child trace hierarchical view functionality
"""
import pytest
from uuid import uuid4
from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trace import Trace
from app.models.project import Project
from app.models.organization import Organization
from app.models.user import User


@pytest.mark.asyncio
async def test_list_traces_with_parent_child_hierarchy(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    test_organization: Organization,
    test_project: Project,
):
    """Test that parent traces show aggregated children data"""

    # Create parent trace
    parent_trace = Trace(
        trace_id=str(uuid4()),
        name="call_insights",
        status="success",
        project_id=test_project.id,
        trace_metadata={
            "source": "Call Insights",
            "stage_count": 3
        },
        total_tokens=0,  # Will be aggregated from children
        total_cost=0.0,
        created_at=datetime.utcnow(),
    )
    db_session.add(parent_trace)
    await db_session.flush()

    # Create 3 child traces
    child_traces = []
    stages = ["fact_extraction", "reasoning", "summary"]
    for i, stage in enumerate(stages):
        child = Trace(
            trace_id=str(uuid4()),
            name=f"call_insights_stage_{i+1}",
            status="success",
            project_id=test_project.id,
            model_name="gpt-4o-mini",
            trace_metadata={
                "parent_trace_id": parent_trace.trace_id,
                "stage": stage,
                "source": "Call Insights"
            },
            total_tokens=1000 + (i * 500),
            total_cost=0.001 + (i * 0.0005),
            total_duration_ms=500 + (i * 200),
            created_at=datetime.utcnow(),
        )
        db_session.add(child)
        child_traces.append(child)

    await db_session.commit()

    # Request trace list
    response = await async_client.get(
        "/api/v1/traces",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Should only show parent trace in top-level list
    assert len(data["traces"]) == 1
    parent = data["traces"][0]

    # Verify parent trace fields
    assert parent["trace_id"] == parent_trace.trace_id
    assert parent["source"] == "Call Insights"
    assert parent["has_children"] is True
    assert parent["child_count"] == 3
    assert len(parent["children"]) == 3

    # Verify aggregated data
    assert parent["aggregated_data"] is not None
    agg = parent["aggregated_data"]
    assert agg["total_tokens"] == 1000 + 1500 + 2000  # Sum of children
    assert abs(agg["total_cost"] - (0.001 + 0.0015 + 0.002)) < 0.0001
    assert "gpt-4o-mini" in agg["model_names"]
    assert agg["avg_duration_ms"] is not None

    # Verify children
    for i, child in enumerate(parent["children"]):
        assert child["parent_trace_id"] == parent_trace.trace_id
        assert child["stage"] == stages[i]
        assert child["has_children"] is False
        assert child["aggregated_data"] is None


@pytest.mark.asyncio
async def test_list_traces_with_source_filter(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    test_project: Project,
):
    """Test filtering traces by source"""

    # Create traces with different sources
    insights_trace = Trace(
        trace_id=str(uuid4()),
        name="insights_trace",
        status="success",
        project_id=test_project.id,
        trace_metadata={"source": "Call Insights"},
        created_at=datetime.utcnow(),
    )
    playground_trace = Trace(
        trace_id=str(uuid4()),
        name="playground_trace",
        status="success",
        project_id=test_project.id,
        trace_metadata={"source": "Playground"},
        created_at=datetime.utcnow(),
    )
    other_trace = Trace(
        trace_id=str(uuid4()),
        name="other_trace",
        status="success",
        project_id=test_project.id,
        trace_metadata={},  # No source = "Other"
        created_at=datetime.utcnow(),
    )

    db_session.add_all([insights_trace, playground_trace, other_trace])
    await db_session.commit()

    # Filter by Call Insights
    response = await async_client.get(
        "/api/v1/traces?source_filter=Call Insights",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["traces"]) == 1
    assert data["traces"][0]["source"] == "Call Insights"

    # Filter by Playground
    response = await async_client.get(
        "/api/v1/traces?source_filter=Playground",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["traces"]) == 1
    assert data["traces"][0]["source"] == "Playground"

    # Filter by Other
    response = await async_client.get(
        "/api/v1/traces?source_filter=Other",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["traces"]) == 1
    assert data["traces"][0]["source"] == "Other"


@pytest.mark.asyncio
async def test_list_traces_excludes_child_traces(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    test_project: Project,
):
    """Test that child traces are not shown at top level"""

    parent = Trace(
        trace_id=str(uuid4()),
        name="parent",
        status="success",
        project_id=test_project.id,
        trace_metadata={"source": "Call Insights"},
        created_at=datetime.utcnow(),
    )
    db_session.add(parent)
    await db_session.flush()

    child = Trace(
        trace_id=str(uuid4()),
        name="child",
        status="success",
        project_id=test_project.id,
        trace_metadata={
            "parent_trace_id": parent.trace_id,
            "source": "Call Insights"
        },
        created_at=datetime.utcnow(),
    )
    db_session.add(child)
    await db_session.commit()

    # Request trace list
    response = await async_client.get(
        "/api/v1/traces",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Only parent should be at top level
    assert data["total"] == 1
    assert data["traces"][0]["trace_id"] == parent.trace_id


@pytest.mark.asyncio
async def test_list_traces_standalone_trace(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    test_project: Project,
):
    """Test that standalone traces (no children) work correctly"""

    standalone = Trace(
        trace_id=str(uuid4()),
        name="standalone",
        status="success",
        project_id=test_project.id,
        model_name="gpt-4",
        total_tokens=1500,
        total_cost=0.05,
        total_duration_ms=750,
        trace_metadata={"source": "Playground"},
        created_at=datetime.utcnow(),
    )
    db_session.add(standalone)
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/traces",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["traces"]) == 1
    trace = data["traces"][0]

    assert trace["has_children"] is False
    assert trace["child_count"] == 0
    assert trace["children"] == []
    assert trace["aggregated_data"] is None
    assert trace["total_tokens"] == 1500
    assert trace["total_cost"] == 0.05
    assert trace["model_name"] == "gpt-4"


@pytest.mark.asyncio
async def test_trace_detail_shows_correct_evaluations(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    test_project: Project,
):
    """Test that trace detail endpoint still works for parent and child traces"""

    # Create parent with evaluations
    parent = Trace(
        trace_id=str(uuid4()),
        name="parent",
        status="success",
        project_id=test_project.id,
        trace_metadata={"source": "Call Insights"},
        created_at=datetime.utcnow(),
    )
    db_session.add(parent)
    await db_session.flush()

    # Create child (no evaluations)
    child = Trace(
        trace_id=str(uuid4()),
        name="child",
        status="success",
        project_id=test_project.id,
        trace_metadata={
            "parent_trace_id": parent.trace_id,
            "stage": "fact_extraction",
            "source": "Call Insights"
        },
        created_at=datetime.utcnow(),
    )
    db_session.add(child)
    await db_session.commit()

    # Get parent detail - should show evaluations
    parent_response = await async_client.get(
        f"/api/v1/traces/{parent.id}/detail",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert parent_response.status_code == 200
    parent_data = parent_response.json()
    assert "evaluations" in parent_data

    # Get child detail - should show 0 evaluations (expected behavior)
    child_response = await async_client.get(
        f"/api/v1/traces/{child.id}/detail",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert child_response.status_code == 200
    child_data = child_response.json()
    assert child_data["evaluations"] == []
