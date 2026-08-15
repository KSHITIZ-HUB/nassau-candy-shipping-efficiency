# Nassau Candy Distributor — Shipping Efficiency Analysis

## 1. Business Problem
The project evaluates shipping performance and identifies routes/geographies and shipping modes that appear faster or slower. The goal is to provide a dashboard that supports operational investigation.

## 2. Dataset
- 10,194 rows
- 18 original fields
- 8,549 unique orders
- 5,044 unique customers
- 15 products
- 59 states/provinces
- 542 cities
- 4 shipping modes
- 4 customer regions

## 3. Core KPIs
- Shipping Lead Time = Ship Date − Order Date
- Average Lead Time = mean lead time by route
- Route Volume = number of shipment rows/orders represented by a route
- Delay Frequency = share of records exceeding the selected threshold
- Route Efficiency Score = fastest-route average lead time divided by route average lead time × 100

## 4. Data Quality Finding
The source file has no duplicate rows and no missing values in the inspected fields. However, shipment dates are much later than order dates: order dates span 2024–2025 while shipment dates span 2026–2030. Consequently, calculated lead times are roughly 904–1,642 days.

This is a critical source-data validation issue. The project should not present these absolute durations as realistic logistics lead times until the source dates are confirmed.

## 5. Route Definition
No factory/origin field exists in the supplied dataset. A true factory-to-customer route cannot therefore be calculated. The dashboard uses customer Region → State/Province as a transparent substitute.

## 6. Recommended Business Use
Use the dashboard to compare relative patterns and identify records/geographies for investigation, while treating absolute lead-time values as provisional until shipment dates are corrected.
