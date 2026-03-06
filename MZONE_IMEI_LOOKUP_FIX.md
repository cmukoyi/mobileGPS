# MZone IMEI Lookup - Critical Fix Documentation

## Problem Overview
**Issue**: Users' vehicles not showing up in the app even though IMEI is registered in database.

**Root Cause**: MZone API stores IMEI in **TWO DIFFERENT FIELDS**, but our code was only checking ONE field.

---

## MZone API Vehicle Response Structure

```json
{
    "id": "a8c9bcac-88bf-451e-80f7-47fdb910b677",
    "description": "350612076585304 (2025-11-20)",
    "registration": "350612076585304",          ← IMEI CAN BE HERE
    "unit_Description": "350612076585304",      ← OR HERE (or both!)
    "ignitionOn": false,
    "lastKnownPosition": {
        "longitude": -1.63916,
        "latitude": 54.95628,
        "utcTimestamp": "2026-03-06T20:11:46Z",
        "speed": 0.00
    }
}
```

### CRITICAL: IMEI Location in MZone Response
The IMEI can appear in:
1. **`registration`** field - Most common
2. **`unit_Description`** field - Also used by MZone
3. **BOTH** fields - Sometimes duplicated

**You MUST check BOTH fields to find all vehicles!**

---

## The Fix

### Before (BROKEN):
```python
for vehicle in all_vehicles:
    registration = vehicle.get('registration', '')
    if registration in user_imeis:  # ❌ Only checking registration
        matched_vehicles.append(vehicle)
```

### After (FIXED):
```python
for vehicle in all_vehicles:
    registration = vehicle.get('registration', '')
    unit_description = vehicle.get('unit_Description', '')
    
    # Check BOTH fields - IMEI can be in either one!
    if registration in user_imeis or unit_description in user_imeis:
        matched_vehicles.append(vehicle)
```

---

## Complete Workflow

### 1. Get All Vehicles from MZone
```python
from app.services.mzone_service import MZoneService

mzone = MZoneService()
vehicles_data = mzone.get_all_vehicles()
all_vehicles = vehicles_data.get('value', [])
```

**API Endpoint**: `GET https://live.mzoneweb.net/mzone62.api/Vehicles?vehicleGroup_Id={group_id}`

### 2. Search for User's IMEIs in BOTH Fields
```python
user_imeis = ['861778061389127', '780901703178395']

matched_vehicles = []
for vehicle in all_vehicles:
    reg = vehicle.get('registration', '')
    unit_desc = vehicle.get('unit_Description', '')
    
    # Check BOTH fields
    if reg in user_imeis or unit_desc in user_imeis:
        matched_vehicles.append(vehicle)
        vehicle_ids.append(vehicle.get('id'))
```

### 3. Get Last Known Position for Matched Vehicles
```python
# Use the vehicle ID to get position
vehicle_id = vehicle.get('id')

# API call:
# GET https://live.mzoneweb.net/mzone62.api/LastKnownPositions?$format=json&$filter=vehicle_Id eq {vehicle_id}

locations_data = mzone.get_vehicle_locations(vehicle_ids)
```

### 4. Merge Location Data
```python
locations = {loc.get('vehicle_Id'): loc for loc in locations_data.get('value', [])}

for vehicle in matched_vehicles:
    vehicle_id = vehicle.get('id')
    if vehicle_id in locations:
        vehicle['lastKnownPosition'] = locations[vehicle_id]
```

---

## Testing the Fix

### Test on Production Server:
```bash
ssh root@161.35.38.209
cd /root/gps-tracker

# Test with specific IMEI
docker-compose exec backend python -c "
from app.services.mzone_service import MZoneService

mzone = MZoneService()
mzone.debug = True

# Get all vehicles
vehicles_data = mzone.get_all_vehicles()
all_vehicles = vehicles_data.get('value', [])

# Search for IMEI in BOTH fields
target_imei = '861778061389127'
print(f'\nSearching for IMEI: {target_imei}')

for v in all_vehicles:
    reg = v.get('registration', '')
    unit_desc = v.get('unit_Description', '')
    
    if target_imei in [reg, unit_desc]:
        print(f'\n✅ FOUND!')
        print(f'  ID: {v.get(\"id\")}')
        print(f'  registration: {reg}')
        print(f'  unit_Description: {unit_desc}')
        print(f'  description: {v.get(\"description\")}')
        break
"
```

### Test After Fix Deployment:
```bash
# Restart backend to load new code
docker-compose restart backend

# Login as test user and verify vehicles appear
# Or use API directly:
curl -X POST https://pinplot.me/api/vehicles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Files Modified

### `/gps-tracker/backend/app/services/mzone_service.py`
**Function**: `get_vehicles_with_locations()`

**Changes**:
1. Added `unit_Description` field check alongside `registration`
2. Updated debug logging to show both fields
3. Added comment explaining MZone stores IMEI in either field

**Lines**: ~200-215

---

## Why This Keeps Breaking

This issue has been "fixed" multiple times because:

1. **Inconsistent MZone Data**: MZone doesn't consistently use the same field
2. **No Documentation**: MZone API docs don't clearly state both fields are used
3. **Copy-Paste Errors**: When fixing other parts, code gets copied that only checks `registration`
4. **Testing Blind Spot**: Test vehicles happened to use `registration` field only

---

## Prevention Checklist

When working with MZone vehicle lookups, ALWAYS:

- [ ] Check **BOTH** `registration` AND `unit_Description` fields
- [ ] Test with multiple IMEIs (some will be in different fields)
- [ ] Add debug logging showing both field values
- [ ] Document which field matched (for debugging)
- [ ] Review this file before making changes to vehicle filtering logic

---

## Related Code Locations

1. **MZone Service**: `/gps-tracker/backend/app/services/mzone_service.py`
   - Function: `get_vehicles_with_locations()`
   - Lines: ~173-260

2. **API Endpoint**: `/gps-tracker/backend/app/main.py`
   - Endpoint: `POST /api/vehicles`
   - Lines: ~1069-1170
   - Calls: `mzone_service.get_vehicles_with_locations(user_imeis)`

3. **Database Models**: `/gps-tracker/backend/app/models.py`
   - Model: `BLETag`
   - Field: `imei` (stores user's registered IMEIs)

---

## Quick Reference Commands

### Check User's IMEIs in Database:
```sql
SELECT imei, device_name, is_active 
FROM ble_tags 
WHERE user_id = (SELECT id FROM users WHERE email = 'user@example.com');
```

### Check MZone for Specific IMEI:
```bash
docker-compose exec backend python -c "
from app.services.mzone_service import MZoneService
mzone = MZoneService()
vehicles = mzone.get_all_vehicles().get('value', [])
imei = '861778061389127'
found = [v for v in vehicles if imei in [v.get('registration'), v.get('unit_Description')]]
print(found if found else 'Not found')
"
```

### Force Backend to Restart:
```bash
cd /root/gps-tracker
docker-compose restart backend
docker-compose logs -f backend | grep "Application startup complete"
```

---

## Summary

**THE FIX**: Always check `registration` **OR** `unit_Description` when matching IMEIs.

**WHY IT MATTERS**: MZone stores IMEIs in either field - missing one means missing vehicles.

**HOW TO REMEMBER**: Search for "registration OR unit_Description" - it's a logical OR, not AND!

---

*Last Updated: March 6, 2026*
*Fixed By: Carl Mukoyi*
*Times This Has Been "Fixed" Before: 10+*
*This Time It's Documented: YES ✅*
