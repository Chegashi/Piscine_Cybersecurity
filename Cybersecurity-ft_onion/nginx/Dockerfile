FROM alpine:3.24

RUN apk add --no-cache nginx

COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /var/www/html/index.html

CMD ["nginx", "-g", "daemon off;"]
