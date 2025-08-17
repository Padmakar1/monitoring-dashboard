FROM prom/alertmanager:v0.25.0

# Install gomplate (static binary)
# Use a small download; adjust version as needed
ARG GOMPLATE_VERSION="v3.11.0"
RUN apk add --no-cache curl ca-certificates \
  && curl -fsSL -o /tmp/gomplate.tar.gz "https://github.com/hairyhenderson/gomplate/releases/download/${GOMPLATE_VERSION}/gomplate_linux-amd64.tar.gz" \
  && tar -xzf /tmp/gomplate.tar.gz -C /tmp \
  && mv /tmp/gomplate /usr/local/bin/gomplate \
  && chmod +x /usr/local/bin/gomplate \
  && rm -rf /tmp/gomplate* \
  && apk del curl

# Copy entrypoint and templates into image (compose mounts will override, but ensure they exist)
COPY docker-entrypoint.sh /etc/alertmanager/docker-entrypoint.sh
COPY config.tmpl /etc/alertmanager/config.tmpl
COPY templates /etc/alertmanager/templates
RUN chmod +x /etc/alertmanager/docker-entrypoint.sh

ENTRYPOINT ["/bin/sh","/etc/alertmanager/docker-entrypoint.sh"]
CMD ["/bin/alertmanager", "--config.file=/etc/alertmanager/config.yml", "--storage.path=/alertmanager"]
