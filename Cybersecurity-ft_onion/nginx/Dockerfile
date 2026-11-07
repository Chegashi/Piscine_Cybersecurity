FROM alpine:3.24

# Upgrade base packages so the image ships the latest security fixes
RUN apk upgrade --no-cache && \
    apk add --no-cache nginx && \
    mkdir -p /var/www/html /run/nginx

COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /var/www/html/index.html
RUN chown -R nginx:nginx /var/www/html && \
    chmod 755 /var/www/html && \
    chmod 644 /var/www/html/index.html

EXPOSE 80
STOPSIGNAL SIGQUIT
CMD ["nginx", "-g", "daemon off;"]
