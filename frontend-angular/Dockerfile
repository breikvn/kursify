# Angular Frontend (Node.js)
FROM node:18

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

# Angular Dev Server starten
CMD ["npm", "start"]
