/**
 * E2E smoke tests for Events feature (v0.3).
 * 
 * Tests:
 * - Events API endpoints (/v1/events, /v1/events/{id})
 * - Events feed.json with audience split
 * - Roadmaps compare API
 * - Admin review endpoints (success & error paths)
 */
import { test, expect } from '@playwright/test';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

test.describe('Events API', () => {
  test('GET /v1/events returns list with pagination', async ({ request }) => {
    const response = await request.get(`${API_BASE}/v1/events?limit=10`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('total');
    expect(data).toHaveProperty('skip');
    expect(data).toHaveProperty('limit');
    expect(data).toHaveProperty('results');
    expect(Array.isArray(data.results)).toBe(true);
  });

  test('GET /v1/events filters by tier', async ({ request }) => {
    const response = await request.get(`${API_BASE}/v1/events?tier=A&limit=5`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    // If any results, verify all are A-tier
    if (data.results.length > 0) {
      data.results.forEach((event: any) => {
        expect(event.evidence_tier).toBe('A');
      });
    }
  });

  test('GET /v1/events/{id} returns event details (or 404)', async ({ request }) => {
    // Try to get event #1, expect 200 or 404 (both valid if no events yet)
    const response = await request.get(`${API_BASE}/v1/events/1`);
    
    if (response.status() === 200) {
      const data = await response.json();
      expect(data).toHaveProperty('id');
      expect(data).toHaveProperty('title');
      expect(data).toHaveProperty('evidence_tier');
      expect(data).toHaveProperty('signpost_links');
      expect(data).toHaveProperty('entities');
      expect(Array.isArray(data.signpost_links)).toBe(true);
    } else {
      expect(response.status()).toBe(404);
    }
  });
});

test.describe('Events Feed', () => {
  test('GET /v1/events/feed.json (public audience) returns A/B tier only', async ({ request }) => {
    const response = await request.get(`${API_BASE}/v1/events/feed.json?audience=public`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('version');
    expect(data).toHaveProperty('license');
    expect(data).toHaveProperty('audience');
    expect(data.audience).toBe('public');
    expect(data).toHaveProperty('items');
    expect(Array.isArray(data.items)).toBe(true);
    
    // Verify all items are A or B tier
    data.items.forEach((item: any) => {
      expect(['A', 'B']).toContain(item.tier);
    });
  });

  test('GET /v1/events/feed.json (research audience) includes all tiers', async ({ request }) => {
    const response = await request.get(`${API_BASE}/v1/events/feed.json?audience=research`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.audience).toBe('research');
    expect(data).toHaveProperty('policy');
    expect(data.policy).toContain('All tiers included');
  });
});

test.describe('Roadmaps Compare API', () => {
  test('GET /v1/roadmaps/compare returns signpost comparisons', async ({ request }) => {
    const response = await request.get(`${API_BASE}/v1/roadmaps/compare`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('generated_at');
    expect(data).toHaveProperty('signposts');
    expect(Array.isArray(data.signposts)).toBe(true);
    
    // If any signposts, verify structure
    if (data.signposts.length > 0) {
      const sp = data.signposts[0];
      expect(sp).toHaveProperty('signpost_code');
      expect(sp).toHaveProperty('current_value');
      expect(sp).toHaveProperty('roadmap_comparisons');
      expect(Array.isArray(sp.roadmap_comparisons)).toBe(true);
    }
  });
});

test.describe('Admin Review Endpoints', () => {
  const ADMIN_KEY = process.env.ADMIN_API_KEY || 'test-admin-key';

  test('POST /v1/admin/events/{id}/approve requires API key', async ({ request }) => {
    // Without API key, expect 422 (missing header) or 403 (invalid)
    const response = await request.post(`${API_BASE}/v1/admin/events/1/approve`);
    expect([422, 403]).toContain(response.status());
  });

  test('POST /v1/admin/events/{id}/approve with key returns 200 or 404', async ({ request }) => {
    const response = await request.post(`${API_BASE}/v1/admin/events/1/approve`, {
      headers: {
        'X-API-Key': ADMIN_KEY
      }
    });
    
    // Expect 200 (success) or 404 (event not found) - both valid
    expect([200, 404]).toContain(response.status());
  });

  test('POST /v1/admin/events/{id}/reject requires reason query param', async ({ request }) => {
    const response = await request.post(`${API_BASE}/v1/admin/events/1/reject`, {
      headers: {
        'X-API-Key': ADMIN_KEY
      }
    });
    
    // Expect 422 (missing reason) or 404 (event not found)
    expect([422, 404]).toContain(response.status());
  });

  test('POST /v1/admin/events/{id}/reject with reason returns 200 or 404', async ({ request }) => {
    const response = await request.post(`${API_BASE}/v1/admin/events/1/reject?reason=Test+rejection`, {
      headers: {
        'X-API-Key': ADMIN_KEY
      }
    });
    
    // Expect 200 (success) or 404 (event not found)
    expect([200, 404]).toContain(response.status());
  });
});

test.describe('Events API Error Handling', () => {
  test('GET /v1/events with invalid tier returns 422', async ({ request }) => {
    const response = await request.get(`${API_BASE}/v1/events?tier=X`);
    expect(response.status()).toBe(422);
  });

  test('GET /v1/events with invalid limit is clamped to max 100', async ({ request }) => {
    const response = await request.get(`${API_BASE}/v1/events?limit=9999`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    // Should return at most 100 items even though we requested 9999
    expect(data.limit).toBeLessThanOrEqual(100);
  });

  test('GET /v1/events/feed.json with invalid audience returns 422', async ({ request }) => {
    const response = await request.get(`${API_BASE}/v1/events/feed.json?audience=invalid`);
    expect(response.status()).toBe(422);
  });
});

