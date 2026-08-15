# Nassau Candy Shipping Efficiency Project

## Objective
Analyze shipping efficiency, route performance, geographic bottlenecks, and ship-mode performance using the supplied Nassau Candy Distributor CSV.

## Important data limitation
The dataset contains customer geography but no factory/origin-location field. Therefore the application defines a route as:

**Customer Region → Customer State/Province**

rather than a true factory-to-customer route.

The supplied dates also require validation: order dates are in 2024–2025 while ship dates are in 2026–2030. This creates very large positive lead times. The dashboard intentionally surfaces this as a data-quality warning instead of silently changing the values.

## Dashboard modules
1. Executive KPI overview
2. Data quality audit
3. Route efficiency ranking
4. Geographic bottleneck analysis
5. Ship-mode comparison
6. Route drill-down
7. Decision-support recommendations

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Place `Nassau Candy Distributor.csv` in the same directory as `app.py`.
