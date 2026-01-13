FROM node:18-alpine

WORKDIR /app

# 複製 package files
COPY package*.json ./

# 安裝依賴
RUN npm install

# 複製應用代碼
COPY . .

# 暴露端口
EXPOSE 5173

# 啟動開發服務器
CMD ["npm", "run", "dev", "--", "--host"]
