import React from 'react'
import { motion } from 'framer-motion'
import { Card } from './UI'

const HistoryPage = () => {
  // This would typically load from an API
  const history = [
    {
      id: 1,
      type: 'email_sent',
      description: 'Sent email to john@example.com',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      icon: '📤',
    },
    {
      id: 2,
      type: 'reminder_created',
      description: 'Created reminder for John\'s birthday',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
      icon: '🔔',
    },
    {
      id: 3,
      type: 'contact_added',
      description: 'Added Jane Doe to contacts',
      timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
      icon: '👥',
    },
  ]

  return (
    <div>
      <h3 className="text-lg font-bold mb-6">Activity History</h3>
      <motion.div
        className="space-y-3 max-h-96 overflow-y-auto"
        initial="hidden"
        animate="show"
        variants={{
          show: {
            transition: {
              staggerChildren: 0.1,
            },
          },
        }}
      >
        {history.map((item) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Card className="flex items-start gap-4">
              <div className="text-2xl">{item.icon}</div>
              <div className="flex-1">
                <p className="font-semibold text-white">{item.description}</p>
                <p className="text-xs text-white/50 mt-1">
                  {item.timestamp.toLocaleString()}
                </p>
              </div>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}

export default HistoryPage
