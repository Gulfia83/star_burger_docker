FROM node:16-alpine

WORKDIR /opt/star-burger

COPY . .

RUN npm ci --dev

CMD ["./node_modules/.bin/parcel", "build", "bundles-src/index.js", "--dist-dir", "bundles", "--public-url=./"]