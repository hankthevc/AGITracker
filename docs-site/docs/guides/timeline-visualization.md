# Timeline Visualization Guide

Visualize AI progress over time with interactive charts showing event frequency, significance, and trends.

## Overview

The Timeline page provides visual analytics of AI developments:

- **Scatter plot**: Individual events plotted by date and significance
- **Cumulative view**: Progress over time by category
- **Filtering**: Focus on specific tiers, categories, or date ranges
- **Export**: Download charts as images or data as CSV

Access at: http://localhost:3000/timeline

## Chart Types

### Scatter View

**What it shows**:
- Each point = one event
- X-axis = publication date
- Y-axis = significance score (0.0-1.0)
- Color = evidence tier (A=green, B=blue, C=yellow, D=red)
- Size = number of signposts affected

**Use cases**:
- Spot clusters of activity (research breakthroughs)
- Identify outlier events (unexpected developments)
- Compare tier distribution over time

**Example**: GPT-5 release creates cluster of A/B tier events in October 2025

### Cumulative View

**What it shows**:
- Progress accumulation over time
- Separate lines for each category
- Smoothed trends (7-day moving average)
- Milestone markers for key thresholds

**Use cases**:
- Track velocity of progress (accelerating or decelerating?)
- Compare category advancement rates
- Forecast future milestones

**Example**: Capabilities line shows sharp increase after GPT-5, while Security remains flat

## Interacting with the Timeline

### Hovering

Hover over any point to see:

```
GPT-5 Achieves 85% on SWE-bench
Date: 2025-10-15
Tier: A-tier (Peer-reviewed)
Significance: 0.85
Signposts: swebench_70, swebench_90
```

### Clicking

Click a point to:
1. Navigate to full event details
2. See AI-generated impact analysis
3. View linked signposts
4. Access source URL

### Zooming

**Desktop**:
- Scroll to zoom in/out
- Click and drag to pan
- Double-click to reset zoom

**Mobile**:
- Pinch to zoom
- Two-finger drag to pan
- Tap reset button to restore

### Filtering

Filter by:

**Evidence Tier**:
```
☑ A-tier  ☑ B-tier  ☐ C-tier  ☐ D-tier
```

**Category**:
```
☑ Capabilities  ☑ Agents  ☑ Inputs  ☑ Security
```

**Date Range**:
- Slider: Drag to select range
- Inputs: Type specific dates
- Presets: Last 3/6/12 months

**Example**: Show only A-tier capabilities events from last 6 months

## Understanding the Data

### Significance Scoring

Events are positioned on Y-axis by significance:

| Y-Position | Score | Interpretation |
|------------|-------|----------------|
| 0.9-1.0 | **Critical** | Major SOTA breakthrough |
| 0.7-0.9 | **High** | Significant progress (10+ point gain) |
| 0.5-0.7 | **Medium** | Moderate advance |
| 0.3-0.5 | **Low** | Incremental improvement |
| 0.0-0.3 | **Minimal** | Contextual, no direct impact |

### Clustering Patterns

**Vertical clusters** (same date):
- Multiple papers from same conference
- Lab release with accompanying blog posts
- Media coverage of single event (C/D tier)

**Horizontal clusters** (same significance):
- Similar-impact developments
- Incremental benchmarking papers
- Routine model releases

**Sparse regions**:
- Research dry spells
- Pre-conference periods
- Holiday slowdowns

### Trend Lines

Cumulative view shows smoothed trends:

**Accelerating** (curve upward):
- Progress speeding up
- Example: Capabilities in 2024-2025 post-GPT-4

**Decelerating** (curve downward):
- Progress slowing
- Example: Some benchmarks approaching saturation

**Linear**:
- Steady progress rate
- Example: Training compute (Moore's law)

**Flat**:
- Stagnant or insufficient data
- Example: Security maturity (lacking evidence)

## Advanced Features

### Time Series Analysis

Toggle **Statistics Panel** to see:

```
Events per Month:
Jan: 12  Feb: 15  Mar: 8  Apr: 22  ...

Average Significance:
Jan: 0.52  Feb: 0.61  Mar: 0.48  Apr: 0.73  ...

Tier Distribution:
A: 45%  B: 30%  C: 20%  D: 5%
```

### Velocity Indicators

Show **velocity overlays** to see:

- **Green arrows**: Acceleration (progress speeding up)
- **Red arrows**: Deceleration (progress slowing)
- **Flat line**: Constant velocity

**Example**: Capabilities shows green arrow in Q4 2024 (GPT-4, Claude 3 releases)

### Milestone Markers

Vertical lines mark key thresholds:

```
|
│ ← SWE-bench 50% (2024-06-15)
│
│ ← SWE-bench 70% (2025-01-20)
│
│ ← SWE-bench 90% (predicted: 2025-12-15)
│
```

Dashed lines = predicted future milestones

### Comparison Mode

Enable **Compare with Forecasts**:

1. Select a forecast source (AI2027, Aschenbrenner, Metaculus)
2. See predicted vs actual overlay
3. Identify "surprise" events (unexpected accelerations)

**Example**: AI2027 predicted SWE-bench 70% by Dec 2025, but achieved Oct 2025 (60 days ahead)

## Exporting Visualizations

### Export Chart as Image

1. Click **Export** button
2. Select **PNG** or **SVG**
3. Choose resolution:
   - Low (1200x800, web)
   - Medium (1920x1080, presentations)
   - High (3840x2160, publications)
4. Download file

**Formats**:
- **PNG**: Raster, good for slides
- **SVG**: Vector, scalable for papers

### Export Data as CSV

1. Click **Export** → **Data**
2. Get CSV with columns:
   ```
   date,title,significance,tier,category,signposts,url
   2025-10-15,GPT-5 on SWE-bench,0.85,A,capabilities,swebench_70;swebench_90,https://...
   ```
3. Import into Excel, Python, R for custom analysis

### Copy Embed Code

Share interactive chart:

1. Click **Share**
2. Copy iframe code:
   ```html
   <iframe src="https://agi-tracker.vercel.app/timeline?embed=true&tier=A" width="800" height="600"></iframe>
   ```
3. Paste in blog or website

## Mobile Optimization

Timeline is fully responsive:

**Phone** (< 640px):
- Vertical layout
- Tap points for details
- Pinch to zoom
- Filter drawer (bottom sheet)

**Tablet** (640-1024px):
- Horizontal layout
- Side panel for filters
- Touch-optimized controls

**Desktop** (> 1024px):
- Full-featured chart
- Keyboard shortcuts
- Multi-select filters

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Arrow keys` | Pan chart |
| `+` / `-` | Zoom in/out |
| `R` | Reset zoom |
| `F` | Toggle filters panel |
| `S` | Toggle statistics panel |
| `E` | Export chart |
| `C` | Toggle cumulative view |

## Performance Notes

### Large Datasets

For 1,000+ events:

- **Virtualization**: Only visible points rendered
- **Lazy loading**: Load on scroll/zoom
- **Caching**: Cached data refreshes every 10 min
- **Decimation**: Downsample for initial view

**Expected performance**:
- 100 events: < 100ms render
- 1,000 events: < 500ms render
- 10,000 events: < 2s render

### Optimization Tips

1. **Filter first**: Apply tier/category filters before zooming
2. **Use date ranges**: Limit to relevant time period
3. **Disable overlays**: Turn off velocity/forecasts for faster rendering
4. **Export large datasets**: Use API for >1,000 events

## Troubleshooting

### Chart Not Loading

**Symptom**: Blank white space where chart should be

**Solutions**:
1. Check browser console for errors
2. Verify API endpoint: `curl http://localhost:8000/v1/events`
3. Disable ad blockers (may block Recharts CDN)
4. Try different browser (Chrome, Firefox)

### Points Overlapping

**Symptom**: Too many points in same area

**Solutions**:
1. Zoom in to spread points
2. Filter to specific tier (e.g., A only)
3. Toggle jitter mode (adds slight random offset)
4. Use data table view instead

### Slow Performance

**Symptom**: Lag when zooming or panning

**Solutions**:
1. Apply filters to reduce point count
2. Use date range slider to limit timeframe
3. Disable statistics panel
4. Export data and use local tools (Excel, Matplotlib)

## Use Cases

### Research: Identifying Trends

**Goal**: Detect acceleration in capabilities progress

**Steps**:
1. Open Timeline
2. Toggle **Cumulative View**
3. Select **Capabilities** category only
4. Look for slope changes (steeper = faster progress)
5. Export chart for paper

### Policymaking: Risk Assessment

**Goal**: Check if security lagging behind capabilities

**Steps**:
1. Toggle **Cumulative View**
2. Enable **Capabilities** and **Security** lines
3. Compare slopes and gap
4. Identify if gap widening (risk increasing)
5. Export data for report

### Media: Creating Visualizations

**Goal**: Embed interactive timeline in blog post

**Steps**:
1. Filter to last 12 months
2. Select A/B tier only
3. Click **Share** → **Embed Code**
4. Copy iframe
5. Paste in blog post

### Developer: Building Dashboards

**Goal**: Fetch timeline data for custom visualization

**API**:
```bash
curl "http://localhost:8000/v1/events?since=2024-01-01&tier=A" | \
  jq '[.events[] | {date:.published_at, sig:.significance, tier:.evidence_tier}]'
```

Then plot with your preferred library (D3, Plotly, Matplotlib).

## Best Practices

✅ **Do**:
- Start with cumulative view for big picture
- Use scatter view for event-level details
- Filter to A-tier for verified trends
- Export charts in SVG for publications
- Include date range in chart title

❌ **Don't**:
- Overfit to short-term fluctuations
- Ignore C/D tier clustering (media hype)
- Assume linear extrapolation
- Cherry-pick favorable time ranges
- Forget to cite methodology

## Next Steps

- [Events Feed](/docs/guides/events-feed) - Explore individual events
- [Signpost Deep-Dives](/docs/guides/signpost-deep-dives) - Understand milestones
- [Custom Presets](/docs/guides/custom-presets) - Weight categories differently
- [API Usage](/docs/guides/api-usage) - Build custom visualizations

## Related Resources

- **Chart Library**: [Recharts Documentation](https://recharts.org/)
- **API Endpoint**: `GET /v1/events` ([API Docs](/docs/api/endpoints))
- **Methodology**: [Scoring System](/docs/methodology) (on live site)

