#!/bin/bash
BASE="http://localhost:8000"

echo "--- Adding normal number (+101) ---"
curl -s -L -X POST $BASE/numbers/ \
  -H "Content-Type: application/json" \
  -d '{"e164": "+14155550101", "country_code": "US", "current_carrier": "Verizon"}' | python3 -m json.tool

echo "--- Adding number ending in 8 (+108) ---"
curl -s -L -X POST $BASE/numbers/ \
  -H "Content-Type: application/json" \
  -d '{"e164": "+14155550108", "country_code": "US", "current_carrier": "Verizon"}' | python3 -m json.tool

echo "--- Reserving +101 (AVAILABLE → RESERVED) ---"
curl -s -X PATCH $BASE/numbers/+14155550101/status \
  -H "Content-Type: application/json" \
  -d '{"new_status": "RESERVED", "version": 1}' | python3 -m json.tool

echo "--- Activating +101 (RESERVED → ACTIVE, attestation success expected) ---"
curl -s -X PATCH $BASE/numbers/+14155550101/status \
  -H "Content-Type: application/json" \
  -d '{"new_status": "ACTIVE", "version": 2}' | python3 -m json.tool

echo "--- Reserving +108 (AVAILABLE → RESERVED) ---"
curl -s -X PATCH $BASE/numbers/+14155550108/status \
  -H "Content-Type: application/json" \
  -d '{"new_status": "RESERVED", "version": 1}' | python3 -m json.tool

echo "--- Activating +108 (RESERVED → ACTIVE, attestation failure expected) ---"
curl -s -X PATCH $BASE/numbers/+14155550108/status \
  -H "Content-Type: application/json" \
  -d '{"new_status": "ACTIVE", "version": 2}' | python3 -m json.tool

echo "--- Waiting 3s for Kafka to process events ---"
sleep 3

echo "--- Checking +101 (signature should be populated) ---"
curl -s $BASE/numbers/+14155550101 | python3 -m json.tool

echo "--- Checking +108 (signature should be null) ---"
curl -s $BASE/numbers/+14155550108 | python3 -m json.tool
