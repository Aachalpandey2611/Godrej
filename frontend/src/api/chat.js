import client from './client'

export const sendMessage = (message, session_id = null) =>
  client.post('/chat', { message, session_id })

export const getSessions = () =>
  client.get('/chat/sessions')

export const getHistory = (sessionId) =>
  client.get(`/chat/history/${sessionId}`)

export const deleteSession = (sessionId) =>
  client.delete(`/chat/${sessionId}`)
