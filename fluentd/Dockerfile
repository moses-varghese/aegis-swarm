# Use the official Fluentd image as a base
FROM fluent/fluentd:v1.16-1

# Switch to the root user to install gems
USER root

# Install the Elasticsearch plugin
RUN fluent-gem install fluent-plugin-elasticsearch

# Switch back to the fluentd user
USER fluent