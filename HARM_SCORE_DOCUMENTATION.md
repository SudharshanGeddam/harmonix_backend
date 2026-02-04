# Harm Score Implementation for Ethical Receipts

## Overview

The Harm Score system provides a numeric severity assessment (0–100) for disasters at receipt destinations, enabling prioritization of ethical delivery operations based on disaster urgency.

---

## Architecture

### 1. Core Service: `app/services/harm_score.py`

**Class:** `HarmScoreCalculator`

**Method:** `calculate(disaster_type: Optional[str]) -> int`

**Disaster Type → Harm Score Mapping:**

| Disaster Type | Harm Score | Severity |
|---------------|-----------|----------|
| earthquake | 95 | Critical |
| flood | 90 | Critical |
| cyclone | 85 | High |
| landslide | 80 | High |
| storm | 70 | Moderate |
| None/Unknown | 10 | Baseline |

**Features:**
- Case-insensitive disaster type matching
- Returns integer 0–100
- Handles null/missing values gracefully
- No database dependencies (pure calculation)

---

## Schema Updates

### `app/schemas/receipts.py`

**New Fields Added:**

#### `ReceiptCreate` (Request Model)
```python
disaster_type: Optional[str] = Field(
    None, description="Disaster type for harm score calculation (earthquake|flood|cyclone|landslide|storm)"
)
```

#### `ReceiptResponse` (Response Model)
```python
harm_score: Optional[int] = Field(
    None, ge=0, le=100, description="Disaster severity score (0-100, calculated from disaster_type)"
)
```

**Note:** `harm_score` is calculated on-the-fly and NOT stored in the database. It's computed during request processing and returned in responses.

---

## Router Integration

### `app/routers/receipts.py`

**Changes:**
- Imports `HarmScoreCalculator` from services
- Updated `create_receipt()` endpoint to:
  1. Extract `disaster_type` from request
  2. Calculate harm_score using `HarmScoreCalculator.calculate()`
  3. Attach harm_score to response object
  4. Log disaster type and calculated score

**Endpoint: `POST /api/receipts`**

Request:
```json
{
  "receipt_id": "RECEIPT-001",
  "package_id": "DEMO-001",
  "proof_summary": "Emergency supplies delivered",
  "status": "verified",
  "disaster_type": "flood"
}
```

Response:
```json
{
  "id": "uuid-1",
  "receipt_id": "RECEIPT-001",
  "package_id": "DEMO-001",
  "proof_summary": "Emergency supplies delivered",
  "status": "verified",
  "timestamp": "2026-02-04T23:27:56.306870",
  "harm_score": 90
}
```

---

## Seed Data Integration

### `app/routers/seed_receipts.py`

**Updates:**
- `DemoReceiptData` class now includes `disaster_type` field
- All 10 demo receipts assigned realistic disaster scenarios:

| Receipt ID | Disaster Type | Harm Score | Package Type |
|-----------|--------------|-----------|--------------|
| RECEIPT-001-HOSPITAL | flood | 90 | Hospital critical |
| RECEIPT-002-NGO | earthquake | 95 | NGO critical |
| RECEIPT-003-COMMUNITY-NGO | cyclone | 85 | Community health |
| RECEIPT-004-WAREHOUSE | None | 10 | Warehouse (routine) |
| RECEIPT-005-RETAIL | landslide | 80 | Retail delayed |
| RECEIPT-006-LUXURY | None | 10 | Luxury (routine) |
| RECEIPT-007-GOVT | flood | 90 | Government health |
| RECEIPT-008-FASHION | storm | 70 | Fashion retail |
| RECEIPT-009-GALLERY | None | 10 | Art gallery (routine) |
| RECEIPT-010-MEDICAL-NGO | earthquake | 95 | Medical emergency |

**Endpoint: `POST /api/seed/receipts`**
- Calculates and logs harm_score for each demo receipt
- Includes harm_score in created response objects
- Prevents re-seeding of existing receipts

---

## Usage Examples

### Frontend Implementation

#### Create Receipt with Disaster Type
```javascript
const createReceiptWithDisaster = async (disaster) => {
  const receipt = {
    receipt_id: "RECEIPT-NEW-001",
    package_id: "PKG-001",
    proof_summary: "Medical supplies delivered to affected area",
    status: "verified",
    disaster_type: disaster // "flood", "earthquake", "cyclone", etc.
  };

  const response = await fetch('http://localhost:8000/api/receipts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(receipt)
  });

  const data = await response.json();
  console.log(`Harm Score: ${data.harm_score}`); // 0-100
  return data;
};

// Usage
await createReceiptWithDisaster("flood"); // harm_score: 90
```

#### List Receipts Sorted by Harm Score
```javascript
const getReceiptsByUrgency = async () => {
  const response = await fetch('http://localhost:8000/api/receipts');
  const { receipts } = await response.json();
  
  // Sort by harm_score descending (highest urgency first)
  return receipts.sort((a, b) => (b.harm_score || 0) - (a.harm_score || 0));
};
```

#### Display Harm Score Visually
```javascript
const getHarmLevel = (score) => {
  if (score >= 90) return "🔴 Critical";
  if (score >= 80) return "🟠 High";
  if (score >= 70) return "🟡 Moderate";
  return "🟢 Routine";
};

// Usage in template
<div>{getHarmLevel(receipt.harm_score)}</div>
```

---

## Design Decisions

### ✅ Calculated, Not Stored
- **Rationale:** Harm score is deterministic from `disaster_type`
- **Benefit:** No database schema changes required
- **Flexibility:** Can update scoring rules without data migration
- **Consistency:** Always reflects current rule set

### ✅ Optional Field
- **Rationale:** Not all receipts are disaster-related
- **Baseline:** Missing disaster_type defaults to harm_score of 10
- **Compatibility:** Existing receipts still queryable

### ✅ Simple Rule Set
- **Rationale:** Demo-friendly, explainable
- **Extensibility:** Can add more disaster types as needed
- **Maintainability:** Rules defined in single location

---

## Future Enhancements

1. **Geographic Scoring** - Factor in location-specific disaster risk
2. **Temporal Urgency** - Increase score for active/ongoing disasters
3. **Severity Levels** - Add sub-types (e.g., "minor_flood" vs "severe_flood")
4. **Machine Learning** - Predictive scoring based on historical data
5. **API Integration** - Real-time disaster data from external services (USGS, NOAA, etc.)
6. **Database Storage** - Optionally store harm_score for analytics and audit trails

---

## Testing

### Test Cases

```python
# Test 1: Earthquake (highest severity)
POST /api/receipts
{..., "disaster_type": "earthquake"}
# Expected: harm_score = 95

# Test 2: No disaster
POST /api/receipts
{..., "disaster_type": null}
# Expected: harm_score = 10

# Test 3: Case insensitivity
POST /api/receipts
{..., "disaster_type": "FLOOD"}
# Expected: harm_score = 90

# Test 4: Unknown disaster
POST /api/receipts
{..., "disaster_type": "tornado"}
# Expected: harm_score = 10 (baseline)
```

### Sample Response
```json
{
  "id": "08d6df27-9d7a-470a-8eda-4720074c2283",
  "receipt_id": "TEST-NO-DISASTER",
  "package_id": "TEST-PKG-003",
  "proof_summary": "Test no disaster",
  "status": "verified",
  "timestamp": "2026-02-04T23:28:38.697304",
  "harm_score": 10
}
```

---

## Summary

The Harm Score system provides a lightweight, extensible foundation for prioritizing ethical deliveries based on disaster severity. It integrates seamlessly with the existing receipts API without database schema changes and enables frontend applications to prioritize relief operations intelligently.

