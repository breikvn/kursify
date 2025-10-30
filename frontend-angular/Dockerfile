# Angular Frontend (Node.js)
FROM node:22

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

# Angular Dev Server starten
CMD ["npm", "start"]
