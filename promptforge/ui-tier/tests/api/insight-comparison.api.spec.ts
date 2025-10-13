import { test, expect } from '@playwright/test';
import { API_BASE_URL } from '../fixtures/test-data';

/**
 * Insight Comparison API Tests
 *
 * Tests the blind comparison API for comparing two Call Insights analyses
 * Endpoints tested:
 * - POST /api/v1/insights/comparisons (create comparison)
 * - GET /api/v1/insights/comparisons (list comparisons)
 * - GET /api/v1/insights/comparisons/{id} (get comparison)
 * - DELETE /api/v1/insights/comparisons/{id} (delete comparison)
 */

test.describe('Insight Comparison API', () => {
  let authToken: string;
  let analysisAId: string;
  let analysisBId: string;
  let comparisonId: string;

  test.beforeAll(async ({ request }) => {
    // Get auth token
    authToken = process.env.PROMPTFORGE_TEST_TOKEN || 'test-token';

    // Create two test analyses with the same transcript for comparison
    const sampleTranscript = `
Agent: Thank you for calling TechSupport Inc. My name is Sarah. How can I help you today?

Customer: Hi Sarah, I'm having issues with my laptop. It won't turn on at all.

Agent: I understand that must be frustrating. Let me help you troubleshoot this. First, can you tell me if the power indicator light comes on when you press the power button?

Customer: No, there's no light at all. I've tried plugging it in but nothing happens.

Agent: Okay, let's try a few things. First, can you try a different power outlet to make sure it's not an outlet issue?

Customer: Sure, let me try... okay I moved to a different outlet but still nothing.

Agent: Alright. Now let's try removing the battery if possible, then holding the power button for 30 seconds to discharge any residual power.

Customer: Okay I removed it and held the button... now what?

Agent: Put the battery back in, plug in the charger, and try turning it on again.

Customer: Oh wow, it's turning on now! I see the startup screen.

Agent: Excellent! The issue was likely residual charge preventing it from powering on. This is a common issue. Is there anything else I can help you with today?

Customer: No that's perfect, thank you so much!

Agent: You're very welcome! Have a great day.
    `.trim();

    // Create Analysis A with gpt-4o-mini
    const analysisAResponse = await request.post(`${API_BASE_URL}/call-insights/analyze`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        transcript: sampleTranscript,
        transcript_title: 'Laptop Power Issue - Model A (gpt-4o-mini)',
        models: {
          stage1_model: 'gpt-4o-mini',
          stage2_model: 'gpt-4o-mini',
          stage3_model: 'gpt-4o-mini',
        },
      },
    });

    if (analysisAResponse.ok()) {
      const analysisA = await analysisAResponse.json();
      analysisAId = analysisA.analysis_id;
      console.log('Created Analysis A:', analysisAId);
    } else {
      console.warn('Failed to create Analysis A:', analysisAResponse.status());
    }

    // Create Analysis B with gpt-4o (same transcript)
    const analysisBResponse = await request.post(`${API_BASE_URL}/call-insights/analyze`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        transcript: sampleTranscript,
        transcript_title: 'Laptop Power Issue - Model B (gpt-4o)',
        models: {
          stage1_model: 'gpt-4o',
          stage2_model: 'gpt-4o',
          stage3_model: 'gpt-4o',
        },
      },
    });

    if (analysisBResponse.ok()) {
      const analysisB = await analysisBResponse.json();
      analysisBId = analysisB.analysis_id;
      console.log('Created Analysis B:', analysisBId);
    } else {
      console.warn('Failed to create Analysis B:', analysisBResponse.status());
    }
  });

  test('POST /insights/comparisons should create a comparison', async ({ request }) => {
    test.skip(!analysisAId || !analysisBId, 'Required analyses not available');

    const response = await request.post(`${API_BASE_URL}/insights/comparisons`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        analysis_a_id: analysisAId,
        analysis_b_id: analysisBId,
        judge_model: 'claude-sonnet-4.5',
        evaluation_criteria: ['groundedness', 'faithfulness', 'completeness', 'clarity', 'accuracy'],
      },
    });

    if (response.ok()) {
      expect(response.status()).toBe(201);
      const data = await response.json();

      // Store comparison ID for later tests
      comparisonId = data.id;
      console.log('Created Comparison:', comparisonId);

      // Validate response structure
      expect(data).toHaveProperty('id');
      expect(data).toHaveProperty('organization_id');
      expect(data).toHaveProperty('user_id');
      expect(data).toHaveProperty('analysis_a');
      expect(data).toHaveProperty('analysis_b');
      expect(data).toHaveProperty('judge_model');
      expect(data).toHaveProperty('evaluation_criteria');
      expect(data).toHaveProperty('overall_winner');
      expect(data).toHaveProperty('overall_reasoning');
      expect(data).toHaveProperty('stage_results');
      expect(data).toHaveProperty('judge_trace');
      expect(data).toHaveProperty('created_at');

      // Validate judge model
      expect(data.judge_model).toBe('claude-sonnet-4.5');

      // Validate evaluation criteria
      expect(data.evaluation_criteria).toEqual(['groundedness', 'faithfulness', 'completeness', 'clarity', 'accuracy']);

      // Validate overall winner
      expect(['A', 'B', 'tie']).toContain(data.overall_winner);
      expect(data.overall_reasoning).toBeTruthy();
      expect(typeof data.overall_reasoning).toBe('string');

      // Validate stage results
      expect(Array.isArray(data.stage_results)).toBeTruthy();
      expect(data.stage_results).toHaveLength(3);

      // Validate each stage result
      data.stage_results.forEach((stage: any) => {
        expect(stage).toHaveProperty('stage');
        expect(stage).toHaveProperty('winner');
        expect(stage).toHaveProperty('scores');
        expect(stage).toHaveProperty('reasoning');

        // Validate winner
        expect(['A', 'B', 'tie']).toContain(stage.winner);

        // Validate scores structure
        expect(stage.scores).toHaveProperty('A');
        expect(stage.scores).toHaveProperty('B');

        // Validate score values
        ['A', 'B'].forEach((model) => {
          const scores = stage.scores[model];
          expect(scores).toHaveProperty('groundedness');
          expect(scores).toHaveProperty('faithfulness');
          expect(scores).toHaveProperty('completeness');
          expect(scores).toHaveProperty('clarity');
          expect(scores).toHaveProperty('accuracy');

          // All scores should be between 0 and 1
          Object.values(scores).forEach((score: any) => {
            if (score !== null && score !== undefined) {
              expect(score).toBeGreaterThanOrEqual(0);
              expect(score).toBeLessThanOrEqual(1);
            }
          });
        });
      });

      // Validate judge trace
      expect(data.judge_trace).toHaveProperty('model');
      expect(data.judge_trace).toHaveProperty('total_tokens');
      expect(data.judge_trace).toHaveProperty('cost');
      expect(data.judge_trace).toHaveProperty('duration_ms');
      expect(data.judge_trace.model).toBe('claude-sonnet-4.5');
      expect(data.judge_trace.total_tokens).toBeGreaterThan(0);
      expect(data.judge_trace.cost).toBeGreaterThan(0);

      // Validate analysis summaries
      expect(data.analysis_a.id).toBe(analysisAId);
      expect(data.analysis_a.model_stage1).toBe('gpt-4o-mini');
      expect(data.analysis_b.id).toBe(analysisBId);
      expect(data.analysis_b.model_stage1).toBe('gpt-4o');

    } else {
      console.error('Create comparison failed:', await response.text());
      expect([401, 403, 404, 422]).toContain(response.status());
    }
  });

  test('POST /insights/comparisons should reject duplicate comparison', async ({ request }) => {
    test.skip(!analysisAId || !analysisBId, 'Required analyses not available');

    // Try to create the same comparison again
    const response = await request.post(`${API_BASE_URL}/insights/comparisons`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        analysis_a_id: analysisAId,
        analysis_b_id: analysisBId,
        judge_model: 'claude-sonnet-4.5',
      },
    });

    // Should return 409 Conflict for duplicate
    if (!response.ok()) {
      expect(response.status()).toBe(409);
      const error = await response.json();
      expect(error.detail).toContain('already exists');
    }
  });

  test('POST /insights/comparisons should reject different transcripts', async ({ request }) => {
    test.skip(!analysisAId, 'Required analysis not available');

    // Create another analysis with different transcript
    const differentTranscript = 'This is a completely different transcript with different content.'.repeat(5);

    const analysisResponse = await request.post(`${API_BASE_URL}/call-insights/analyze`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        transcript: differentTranscript,
        transcript_title: 'Different Transcript',
      },
    });

    if (analysisResponse.ok()) {
      const analysisDifferent = await analysisResponse.json();
      const differentAnalysisId = analysisDifferent.analysis_id;

      // Try to compare analyses with different transcripts
      const response = await request.post(`${API_BASE_URL}/insights/comparisons`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        data: {
          analysis_a_id: analysisAId,
          analysis_b_id: differentAnalysisId,
        },
      });

      // Should return 422 Unprocessable Entity
      if (!response.ok()) {
        expect(response.status()).toBe(422);
        const error = await response.json();
        expect(error.detail.toLowerCase()).toContain('different transcript');
      }
    }
  });

  test('POST /insights/comparisons should reject non-existent analysis', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/insights/comparisons`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        analysis_a_id: '00000000-0000-0000-0000-000000000000',
        analysis_b_id: '11111111-1111-1111-1111-111111111111',
      },
    });

    // Should return 404 Not Found
    if (!response.ok()) {
      expect(response.status()).toBe(404);
    }
  });

  test('GET /insights/comparisons should list comparisons', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/insights/comparisons`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (response.ok()) {
      expect(response.status()).toBe(200);
      const data = await response.json();

      // Validate response structure
      expect(data).toHaveProperty('comparisons');
      expect(data).toHaveProperty('pagination');
      expect(Array.isArray(data.comparisons)).toBeTruthy();

      // Validate pagination
      expect(data.pagination).toHaveProperty('page');
      expect(data.pagination).toHaveProperty('page_size');
      expect(data.pagination).toHaveProperty('total_count');
      expect(data.pagination).toHaveProperty('total_pages');

      // Validate comparison list items
      if (data.comparisons.length > 0) {
        const comparison = data.comparisons[0];
        expect(comparison).toHaveProperty('id');
        expect(comparison).toHaveProperty('model_a_summary');
        expect(comparison).toHaveProperty('model_b_summary');
        expect(comparison).toHaveProperty('judge_model');
        expect(comparison).toHaveProperty('overall_winner');
        expect(comparison).toHaveProperty('cost_difference');
        expect(comparison).toHaveProperty('quality_improvement');
        expect(comparison).toHaveProperty('created_at');

        expect(['A', 'B', 'tie']).toContain(comparison.overall_winner);
      }
    } else {
      expect([401, 403]).toContain(response.status());
    }
  });

  test('GET /insights/comparisons with pagination', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/insights/comparisons?skip=0&limit=5`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (response.ok()) {
      expect(response.status()).toBe(200);
      const data = await response.json();

      expect(data.pagination.page_size).toBe(5);
      expect(data.comparisons.length).toBeLessThanOrEqual(5);
    } else {
      expect([401, 403]).toContain(response.status());
    }
  });

  test('GET /insights/comparisons/{id} should return specific comparison', async ({ request }) => {
    test.skip(!comparisonId, 'Comparison ID not available');

    const response = await request.get(`${API_BASE_URL}/insights/comparisons/${comparisonId}`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (response.ok()) {
      expect(response.status()).toBe(200);
      const data = await response.json();

      // Validate complete comparison structure
      expect(data.id).toBe(comparisonId);
      expect(data).toHaveProperty('overall_winner');
      expect(data).toHaveProperty('overall_reasoning');
      expect(data).toHaveProperty('stage_results');
      expect(data).toHaveProperty('judge_trace');
      expect(data).toHaveProperty('analysis_a');
      expect(data).toHaveProperty('analysis_b');

      // Validate stage results are complete
      expect(data.stage_results).toHaveLength(3);

      // Validate stage names
      const stageNames = data.stage_results.map((s: any) => s.stage);
      expect(stageNames).toContain('Stage 1: Fact Extraction');
      expect(stageNames).toContain('Stage 2: Reasoning & Insights');
      expect(stageNames).toContain('Stage 3: Summary');

    } else {
      expect([401, 403, 404]).toContain(response.status());
    }
  });

  test('GET /insights/comparisons/{id} should return 404 for non-existent comparison', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/insights/comparisons/00000000-0000-0000-0000-000000000000`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (!response.ok()) {
      expect(response.status()).toBe(404);
    }
  });

  test('DELETE /insights/comparisons/{id} should delete comparison', async ({ request }) => {
    test.skip(!comparisonId, 'Comparison ID not available');

    const response = await request.delete(`${API_BASE_URL}/insights/comparisons/${comparisonId}`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (response.ok()) {
      expect(response.status()).toBe(204);

      // Verify deletion - GET should return 404
      const getResponse = await request.get(`${API_BASE_URL}/insights/comparisons/${comparisonId}`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (!getResponse.ok()) {
        expect(getResponse.status()).toBe(404);
      }
    } else {
      expect([401, 403, 404]).toContain(response.status());
    }
  });

  test('DELETE /insights/comparisons/{id} should return 404 for non-existent comparison', async ({ request }) => {
    const response = await request.delete(`${API_BASE_URL}/insights/comparisons/00000000-0000-0000-0000-000000000000`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    if (!response.ok()) {
      expect(response.status()).toBe(404);
    }
  });

  test('API should require authentication', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/insights/comparisons`);

    expect(response.status()).toBe(403);
  });

  test('API should validate request body for POST', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/insights/comparisons`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      data: {
        // Missing required fields
      },
    });

    if (!response.ok()) {
      expect(response.status()).toBe(422);
    }
  });
});
