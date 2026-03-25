<template>
  <div class="chat-container">
    <h2>Аналитика ДТП</h2>
    <div class="mode-selector">
      <label>
        <input type="radio" value="local" v-model="mode" />
        Локальная модель (Ollama)
      </label>
      <label>
        <input type="radio" value="cloud" v-model="mode" />
        Облачная модель (DeepSeek API)
      </label>
    </div>
    <div class="chat-messages">
      <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
        <strong>{{ msg.role === 'user' ? 'Вы' : 'AI' }}:</strong>
        <pre v-if="msg.role === 'ai' && msg.sql">{{ msg.sql }}</pre>
        <div v-html="msg.content"></div>
      </div>
    </div>
    <div class="input-area">
      <textarea
        v-model="userInput"
        @keyup.enter="sendMessage"
        placeholder="Спросите что-нибудь о ДТП..."
        rows="3"
      ></textarea>
      <button @click="sendMessage" :disabled="loading">
        {{ loading ? 'Отправка...' : 'Отправить' }}
      </button>
    </div>
    <div v-if="loading" class="loading">Модель думает...</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

interface Message {
  role: 'user' | 'ai'
  content: string
  sql?: string
}

const messages = ref<Message[]>([])
const userInput = ref('')
const loading = ref(false)
const mode = ref('local')   // по умолчанию локальная (или cloud, как удобно)
const sessionId = ref('')   // для хранения идентификатора сессии

const API_URL = 'http://localhost:8000/ask'

const sendMessage = async () => {
  if (!userInput.value.trim()) return

  // Добавляем сообщение пользователя в чат
  messages.value.push({ role: 'user', content: userInput.value })
  const question = userInput.value
  userInput.value = ''
  loading.value = true

  try {
    const response = await axios.post(API_URL, {
      user_question: question,
      mode: mode.value,
      session_id: sessionId.value   // передаём session_id, если есть
    })
    const data = response.data

    // Сохраняем session_id, если он вернулся с сервера
    if (data.session_id && !sessionId.value) {
      sessionId.value = data.session_id
    }

    if (data.success) {
      let content = ''
      if (data.data && data.data.length > 0) {
        content = `<p>${data.message}</p>`
        content += '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">'
        if (data.columns) {
          content += '<thead><tr>' + data.columns.map((col: any) => `<th>${col}</th>`).join('') + '</tr></thead>'
        }
        content += '<tbody>'
        data.data.forEach((row: any) => {
          content += '<tr>' + data.columns.map((col: string | number) => `<td>${row[col] ?? ''}</td>`).join('') + '</tr>'
        })
        content += '</tbody></table>'
      } else {
        content = `<p>${data.message || 'Нет данных'}</p>`
      }
      messages.value.push({
        role: 'ai',
        content: content,
        sql: data.generated_sql
      })
    } else {
      messages.value.push({
        role: 'ai',
        content: `<p style="color:red;">Ошибка: ${data.error}</p>`,
        sql: data.generated_sql
      })
    }
  } catch (error) {
    messages.value.push({
      role: 'ai',
      content: `<p style="color:red;">Ошибка соединения с сервером. Проверьте, запущен ли бэкенд.</p>`
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 20px auto;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 20px;
  font-family: Arial, sans-serif;
}
.mode-selector {
  margin-bottom: 15px;
  display: flex;
  gap: 20px;
}
.mode-selector label {
  cursor: pointer;
}
.chat-messages {
  height: 400px;
  overflow-y: auto;
  border: 1px solid #eee;
  padding: 10px;
  margin-bottom: 10px;
}
.message {
  margin-bottom: 15px;
}
.message.user {
  text-align: right;
  color: blue;
}
.message.ai {
  text-align: left;
  color: green;
}
.message pre {
  background: #f5f5f5;
  padding: 5px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}
.input-area {
  display: flex;
  gap: 10px;
}
textarea {
  flex: 1;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
}
button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:disabled {
  background-color: #aaa;
}
.loading {
  text-align: center;
  margin-top: 10px;
  font-style: italic;
}
table {
  margin-top: 10px;
  width: 100%;
  font-size: 12px;
}
th, td {
  padding: 4px;
  text-align: left;
}
</style>