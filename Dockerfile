# Step 1: Base image
FROM node:20-slim

# Step 2: Working directory സെറ്റ് ചെയ്യുക
WORKDIR /app

# Step 3: Package files കോപ്പി ചെയ്ത് Dependencies ഇൻസ്റ്റാൾ ചെയ്യുക
COPY package*.json ./
RUN npm install --production

# Step 4: ബാക്കി സോഴ്സ് കോഡുകൾ കോപ്പി ചെയ്യുക
COPY . .

# Step 5: ആപ്ലിക്കേഷൻ റൺ ചെയ്യുക
CMD ["npm", "start"]
