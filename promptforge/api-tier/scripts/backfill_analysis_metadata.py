#!/usr/bin/env python3
"""
Backfill analysis_metadata.model_parameters from traces

This script populates the model_parameters field in call_insights_analysis.analysis_metadata
by extracting temperature, top_p, and max_tokens from the child traces.

Usage:
    python scripts/backfill_analysis_metadata.py [--dry-run]
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.call_insights import CallInsightsAnalysis
from app.models.trace import Trace
from app.core.config import settings


async def backfill_analysis_metadata(dry_run: bool = False):
    """Backfill model_parameters in analysis_metadata from child traces"""

    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get all analyses
        result = await session.execute(
            select(CallInsightsAnalysis).order_by(CallInsightsAnalysis.created_at.desc())
        )
        analyses = result.scalars().all()

        print(f"Found {len(analyses)} analyses to process")

        updated_count = 0
        skipped_count = 0
        error_count = 0

        for analysis in analyses:
            try:
                # Check if already has model_parameters
                if (analysis.analysis_metadata and
                    isinstance(analysis.analysis_metadata, dict) and
                    "model_parameters" in analysis.analysis_metadata):
                    print(f"✓ Analysis {analysis.id} already has model_parameters, skipping")
                    skipped_count += 1
                    continue

                # Get parent trace
                if not analysis.parent_trace_id:
                    print(f"⚠ Analysis {analysis.id} has no parent_trace_id, skipping")
                    skipped_count += 1
                    continue

                # Get parent trace to find parent trace_id
                parent_result = await session.execute(
                    select(Trace).where(Trace.id == analysis.parent_trace_id)
                )
                parent_trace = parent_result.scalar_one_or_none()

                if not parent_trace:
                    print(f"⚠ Analysis {analysis.id} parent trace not found, skipping")
                    skipped_count += 1
                    continue

                # Get child traces (stages)
                # Query all traces and filter in Python (JSONB comparison issues)
                all_traces_result = await session.execute(select(Trace))
                all_traces = all_traces_result.scalars().all()

                child_traces = [
                    t for t in all_traces
                    if t.trace_metadata and
                    t.trace_metadata.get("parent_trace_id") == parent_trace.trace_id
                ]
                child_traces.sort(key=lambda t: t.created_at)

                if len(child_traces) < 3:
                    print(f"⚠ Analysis {analysis.id} has only {len(child_traces)} child traces, skipping")
                    skipped_count += 1
                    continue

                # Extract parameters from each stage
                model_parameters = {}
                stage_mapping = {
                    "Stage 1: Fact Extraction": "stage1",
                    "Stage 2: Reasoning & Insights": "stage2",
                    "Stage 3: Summary Synthesis": "stage3",
                }

                for child_trace in child_traces:
                    if not child_trace.trace_metadata:
                        continue

                    stage_name = child_trace.trace_metadata.get("stage")
                    if not stage_name or stage_name not in stage_mapping:
                        continue

                    stage_key = stage_mapping[stage_name]

                    if child_trace.input_data and "parameters" in child_trace.input_data:
                        params = child_trace.input_data["parameters"]
                        model_parameters[stage_key] = {
                            "temperature": params.get("temperature", 0.0),
                            "top_p": params.get("top_p", 0.95),
                            "max_tokens": params.get("max_tokens", 1000),
                        }

                if len(model_parameters) < 3:
                    print(f"⚠ Analysis {analysis.id} could only extract {len(model_parameters)} stages, skipping")
                    skipped_count += 1
                    continue

                # Update analysis_metadata
                updated_metadata = analysis.analysis_metadata or {}
                updated_metadata["model_parameters"] = model_parameters

                if dry_run:
                    print(f"[DRY RUN] Would update analysis {analysis.id}:")
                    print(f"  Stage 1: temp={model_parameters['stage1']['temperature']}, "
                          f"top_p={model_parameters['stage1']['top_p']}, "
                          f"max_tokens={model_parameters['stage1']['max_tokens']}")
                    print(f"  Stage 2: temp={model_parameters['stage2']['temperature']}, "
                          f"top_p={model_parameters['stage2']['top_p']}, "
                          f"max_tokens={model_parameters['stage2']['max_tokens']}")
                    print(f"  Stage 3: temp={model_parameters['stage3']['temperature']}, "
                          f"top_p={model_parameters['stage3']['top_p']}, "
                          f"max_tokens={model_parameters['stage3']['max_tokens']}")
                else:
                    # Execute update
                    await session.execute(
                        update(CallInsightsAnalysis)
                        .where(CallInsightsAnalysis.id == analysis.id)
                        .values(analysis_metadata=updated_metadata)
                    )
                    print(f"✓ Updated analysis {analysis.id} with model_parameters")

                updated_count += 1

            except Exception as e:
                print(f"✗ Error processing analysis {analysis.id}: {e}")
                error_count += 1
                continue

        if not dry_run:
            await session.commit()
            print(f"\n✅ Committed changes to database")

        print(f"\n{'=' * 60}")
        print(f"Summary:")
        print(f"  Total analyses: {len(analyses)}")
        print(f"  Updated: {updated_count}")
        print(f"  Skipped: {skipped_count}")
        print(f"  Errors: {error_count}")
        print(f"{'=' * 60}")

        if dry_run:
            print("\n⚠️  DRY RUN MODE - No changes were made to the database")
            print("Run without --dry-run to apply changes")


async def main():
    parser = argparse.ArgumentParser(description="Backfill analysis_metadata.model_parameters from traces")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")
    args = parser.parse_args()

    print("=" * 60)
    print("Backfill Analysis Metadata - Model Parameters")
    print("=" * 60)
    print()

    if args.dry_run:
        print("⚠️  Running in DRY RUN mode\n")

    await backfill_analysis_metadata(dry_run=args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
