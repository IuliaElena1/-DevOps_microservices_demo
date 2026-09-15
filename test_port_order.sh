#!/bin/bash
INVENTORY="http://localhost:8000"
PORT_ORDER="http://localhost:8001"

echo "=== Step 1: Add test numbers to Inventory ==="

echo "--- Adding normal number (+101) ---"
curl -s -L -X POST $INVENTORY/numbers/ \
  -H "Content-Type: application/json" \
  -d '{"e164": "+14155550101", "country_code": "US", "current_carrier": "Verizon"}' | python3 -m json.tool

echo "--- Adding number ending in 9 (+109) - port will be rejected ---"
curl -s -L -X POST $INVENTORY/numbers/ \
  -H "Content-Type: application/json" \
  -d '{"e164": "+14155550109", "country_code": "US", "current_carrier": "Verizon"}' | python3 -m json.tool

echo "--- Adding number ending in 8 (+108) - attestation will fail ---"
curl -s -L -X POST $INVENTORY/numbers/ \
  -H "Content-Type: application/json" \
  -d '{"e164": "+14155550108", "country_code": "US", "current_carrier": "Verizon"}' | python3 -m json.tool

echo ""
echo "=== Step 2: Check port orders were auto-created by consumer ==="
sleep 2
curl -s $PORT_ORDER/orders/ | python3 -m json.tool

echo ""
echo "=== Step 3: Reserve numbers (start porting) ==="

echo "--- Reserving +101 (should succeed and go ACTIVE eventually) ---"
curl -s -X POST $PORT_ORDER/orders/+14155550101/reserve | python3 -m json.tool

echo "--- Reserving +109 (will be REJECTED by poller - ends in 9) ---"
curl -s -X POST $PORT_ORDER/orders/+14155550109/reserve | python3 -m json.tool

echo "--- Reserving +108 (will port ok but attestation will fail) ---"
curl -s -X POST $PORT_ORDER/orders/+14155550108/reserve | python3 -m json.tool

echo ""
echo "=== Step 4: Waiting 45s for poller to advance all orders ==="
echo "(RESERVED → SUBMITTED_AND_PENDING → APPROVED → ACTIVE, 10s each step)"
sleep 45

echo ""
echo "=== Step 5: Check final port order statuses ==="
echo "--- +101 should be ACTIVE ---"
curl -s $PORT_ORDER/orders/+14155550101 | python3 -m json.tool

echo "--- +109 should be REJECTED (ends in 9) ---"
curl -s $PORT_ORDER/orders/+14155550109 | python3 -m json.tool

echo "--- +108 should be ACTIVE (porting ok, attestation failed separately) ---"
curl -s $PORT_ORDER/orders/+14155550108 | python3 -m json.tool

echo ""
echo "=== Step 6: Check Inventory - numbers should reflect port outcomes ==="
echo "--- +101 should be ACTIVE with signature populated ---"
curl -s $INVENTORY/numbers/+14155550101 | python3 -m json.tool

echo "--- +109 should be AVAILABLE (port rejected, back to pool) ---"
curl -s $INVENTORY/numbers/+14155550109 | python3 -m json.tool

echo "--- +108 should be ACTIVE with signature null (attestation failed) ---"
curl -s $INVENTORY/numbers/+14155550108 | python3 -m json.tool

echo ""
echo "=== Step 7: Test release of active number ==="
echo "--- Releasing +101 ---"
curl -s -X POST $PORT_ORDER/orders/+14155550101/release | python3 -m json.tool

echo "--- +101 should now be RELEASED in both services ---"
curl -s $PORT_ORDER/orders/+14155550101 | python3 -m json.tool
curl -s $INVENTORY/numbers/+14155550101 | python3 -m json.tool
