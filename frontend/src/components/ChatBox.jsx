import React, { useState, useContext, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ChatContext } from '../contexts/ChatContext'
import { mailService, voiceService } from '../services/api'
import { Button, Input } from './UI'

const ChatBox = () => {
  const { messages, addMessage, setCurrentDraft } = useContext(ChatContext)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [draftPreview, setDraftPreview] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, draftPreview])

  const handleSendCommand = async () => {
    if (!input.trim()) return

    // Add user message
    addMessage({
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    })

    setInput('')
    setLoading(true)

    try {
      const response = await mailService.generatePreview(input)
      if (response.data.draft) {
        setDraftPreview(response.data.draft)
        setCurrentDraft(response.data.draft)
        addMessage({
          id: Date.now(),
          role: 'assistant',
          content: 'I\'ve generated an email preview for you. Review it below and click "Send" when ready.',
          draft: response.data.draft,
          timestamp: new Date(),
        })
      }
    } catch (error) {
      addMessage({
        id: Date.now(),
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || 'Failed to process command'}`,
        timestamp: new Date(),
        isError: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleVoiceInput = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setLoading(true)
    try {
      const response = await voiceService.transcribe(file)
      setInput(response.data.transcript || '')
    } catch (error) {
      alert('Failed to transcribe audio')
    } finally {
      setLoading(false)
      e.target.value = ''
    }
  }

  const handleSendEmail = async (draft) => {
    try {
      await mailService.confirmDraft(draft.id, 'send')
      addMessage({
        id: Date.now(),
        role: 'assistant',
        content: '✅ Email sent successfully!',
        timestamp: new Date(),
        isSuccess: true,
      })
      setDraftPreview(null)
    } catch (error) {
      addMessage({
        id: Date.now(),
        role: 'assistant',
        content: `Failed to send: ${error.response?.data?.detail || 'Unknown error'}`,
        timestamp: new Date(),
        isError: true,
      })
    }
  }

  const messageVariants = {
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0 },
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 md:p-6">
        {messages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-center h-full"
          >
            <div className="text-center">
              <div className="text-6xl mb-4">💬</div>
              <h3 className="text-2xl font-bold mb-2">Start Your Conversation</h3>
              <p className="text-white/60 max-w-md">
                Describe the email you want to send, and I'll help you draft it perfectly.
              </p>
            </div>
          </motion.div>
        ) : (
          <>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                variants={messageVariants}
                initial="initial"
                animate="animate"
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs md:max-w-md lg:max-w-lg p-4 rounded-2xl ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-brand-primary to-brand-secondary text-white rounded-br-none'
                      : msg.isError
                      ? 'bg-red-500/20 text-red-300 rounded-bl-none'
                      : msg.isSuccess
                      ? 'bg-green-500/20 text-green-300 rounded-bl-none'
                      : 'glass rounded-bl-none'
                  }`}
                >
                  <p className="text-sm">{msg.content}</p>
                  {msg.draft && (
                    <div className="mt-3 pt-3 border-t border-white/20 space-y-2">
                      <p className="text-xs font-semibold text-white/60">📧 Email Preview</p>
                      <div className="text-xs space-y-1">
                        <p><strong>To:</strong> {msg.draft.recipient_email}</p>
                        <p><strong>Subject:</strong> {msg.draft.subject}</p>
                        <p className="text-xs text-white/70 mt-2 line-clamp-2">{msg.draft.body}</p>
                      </div>
                      <Button
                        variant="primary"
                        size="sm"
                        className="w-full mt-2"
                        onClick={() => handleSendEmail(msg.draft)}
                      >
                        📤 Send Email
                      </Button>
                    </div>
                  )}
                  <span className="text-xs text-white/50 mt-2 block">
                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </motion.div>
            ))}
            {loading && (
              <motion.div
                variants={messageVariants}
                initial="initial"
                animate="animate"
                className="flex justify-start"
              >
                <div className="glass p-4 rounded-2xl rounded-bl-none">
                  <div className="flex gap-2">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        animate={{ y: [0, -10, 0] }}
                        transition={{ duration: 1, delay: i * 0.2 }}
                        className="w-2 h-2 rounded-full bg-brand-primary"
                      />
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-white/10 p-4 md:p-6 bg-dark-900/50 backdrop-blur">
        <div className="flex gap-3">
          <input
            type="file"
            accept="audio/*"
            onChange={handleVoiceInput}
            className="hidden"
            id="voice-input"
          />
          <label htmlFor="voice-input">
            <Button
              variant="secondary"
              size="md"
              className="cursor-pointer"
              as="label"
              disabled={loading}
            >
              🎤
            </Button>
          </label>

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleSendCommand()}
            placeholder="Describe the email you want to send..."
            className="flex-1 px-4 py-3 bg-white/5 border border-white/20 rounded-lg focus:outline-none focus:border-brand-primary focus:ring-2 focus:ring-brand-primary/30 transition-smooth text-white placeholder-white/40"
            disabled={loading}
          />

          <Button
            variant="primary"
            size="md"
            onClick={handleSendCommand}
            disabled={loading || !input.trim()}
          >
            📤 Send
          </Button>
        </div>
      </div>
    </div>
  )
}

export default ChatBox
