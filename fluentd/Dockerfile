# Use the official Fluentd image as a base
FROM fluent/fluentd:v1.16-1

# Switch to the root user to install gems
USER root

RUN apk add --no-cache curl netcat-openbsd 

RUN fluent-gem install fluent-plugin-elasticsearch -v 6.0.0 --no-document && \
    fluent-gem install fluent-plugin-multi-format-parser --no-document && \
    rm -rf /var/cache/apk/*

# Switch back to the fluentd user
USER fluent