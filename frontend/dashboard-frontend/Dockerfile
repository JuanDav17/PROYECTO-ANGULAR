FROM node:18-alpine
WORKDIR /app

# 1. Copia solo package.json y package-lock.json
COPY package*.json ./

# 2. Instala dependencias del proyecto
RUN npm install 

# 3. Copia el resto del proyecto (angular.json, src, etc.)
COPY . .

# Exponer puerto 4200
EXPOSE 4200

# 4. Levantar Angular
# Usa el script 'start' definido en package.json (que es 'ng serve')
CMD ["npm", "run", "start", "--", "--host", "0.0.0.0", "--disable-host-check"]