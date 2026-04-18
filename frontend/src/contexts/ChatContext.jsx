import React, { createContext, useState } from 'react'

export const ChatContext = createContext()

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([])
  const [currentDraft, setCurrentDraft] = useState(null)

  const addMessage = (message) => {
    setMessages(prev => [...prev, message])
  }

  const clearMessages = () => {
    setMessages([])
  }

  return (
    <ChatContext.Provider value={{ messages, addMessage, clearMessages, currentDraft, setCurrentDraft }}>
      {children}
    </ChatContext.Provider>
  )
}
