FROM node:18-slim

WORKDIR /usr/src/app

RUN npm install -g markdownlint-cli

COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
