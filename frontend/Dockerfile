FROM node:26.7.0-alpine AS base
WORKDIR /usr/src/app
COPY ./frontend/package* .
RUN npm install
COPY ./frontend .

FROM base AS dev
EXPOSE 80
CMD ["npm", "run", "dev"]

FROM base AS build
RUN npm run build

FROM nginx:1.31.1-alpine AS prod
COPY --from=build /usr/src/app/dist /usr/share/nginx/html
COPY ./deploy/nginx-frontend.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]