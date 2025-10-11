#!/bin/sh

# Wait for Kibana to be available before attempting to configure it
until curl -s http://kibana:5601/api/status | grep -q '"level":"available"'; do
  echo "Waiting for Kibana to be available..."
  sleep 5
done

echo "Kibana is available. Setting up index pattern..."

# Create the index pattern 'fluentd-*' using the Kibana API
# This command is idempotent; it will not create a duplicate if one already exists.
curl -X POST http://kibana:5601/api/saved_objects/index-pattern/fluentd-\* \
  -H 'kbn-xsrf: true' \
  -H 'Content-Type: application/json' \
  -d '{"attributes": {"title": "fluentd-*", "timeFieldName": "@timestamp"}}'

echo "Kibana setup complete."