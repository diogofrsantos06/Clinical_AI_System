#!/bin/sh
# docker-entrypoint.sh

# Substituir variáveis de ambiente no template nginx
envsubst '${BACKEND_HOST} ${BACKEND_PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Mover o arquivo processado para o local final
mv /etc/nginx/nginx.conf.tmp /etc/nginx/nginx.conf

# Executar o entrypoint padrão do nginx
exec "$@"