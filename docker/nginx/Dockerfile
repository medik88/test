FROM nginx:latest

RUN mkdir -p /app/src/static_content
RUN rm -rf /etc/nginx/conf.d/default.conf
COPY ./conf/api.conf /etc/nginx/conf.d/
COPY ./conf/nginx.conf /etc/nginx/

EXPOSE 80