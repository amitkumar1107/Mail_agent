import React from 'react'
import { motion } from 'framer-motion'
import { Card } from './UI'

const StatCard = ({ icon, label, value, color = 'blue' }) => {
  const colorClasses = {
    blue: 'from-blue-500',
    green: 'from-green-500',
    purple: 'from-purple-500',
    pink: 'from-pink-500',
  }

  return (
    <Card className={`text-center bg-gradient-to-br ${colorClasses[color]}/10 border-l-4 border-${color}-500`}>
      <div className="text-4xl mb-2">{icon}</div>
      <p className="text-white/60 text-sm">{label}</p>
      <p className="text-3xl font-bold gradient-text mt-2">{value}</p>
    </Card>
  )
}

const Dashboard = ({ data }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="space-y-8"
    >
      {/* Stats Grid */}
      <motion.div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div variants={itemVariants}>
          <StatCard
            icon="📧"
            label="Emails Sent"
            value={data?.sent_count || 0}
            color="blue"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            icon="🔔"
            label="Pending Reminders"
            value={data?.pending_reminders_count || 0}
            color="green"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            icon="👥"
            label="Contacts"
            value={data?.contacts_count || 0}
            color="purple"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <StatCard
            icon="📝"
            label="Templates"
            value={data?.templates_count || 0}
            color="pink"
          />
        </motion.div>
      </motion.div>

      {/* Suggestions Section */}
      {data?.suggestions && data.suggestions.length > 0 && (
        <motion.div variants={itemVariants}>
          <Card>
            <h3 className="text-lg font-bold mb-4">💡 AI Suggestions</h3>
            <ul className="space-y-2">
              {data.suggestions.map((suggestion, idx) => (
                <motion.li
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * idx }}
                  className="p-3 bg-white/5 rounded-lg text-sm text-white/80 border-l-2 border-brand-primary"
                >
                  {suggestion}
                </motion.li>
              ))}
            </ul>
          </Card>
        </motion.div>
      )}

      {/* Frequent Contacts */}
      {data?.frequent_contacts && data.frequent_contacts.length > 0 && (
        <motion.div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div variants={itemVariants}>
            <Card>
              <h3 className="text-lg font-bold mb-4">👥 Frequent Contacts</h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {data.frequent_contacts.map((contact, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.05 * idx }}
                    className="flex justify-between items-center p-2 rounded bg-white/5 text-sm"
                  >
                    <span className="text-brand-secondary">{contact.recipient_email}</span>
                    <span className="text-white/60">{contact.count} emails</span>
                  </motion.div>
                ))}
              </div>
            </Card>
          </motion.div>

          {/* Upcoming Events */}
          {data?.upcoming_events && data.upcoming_events.length > 0 && (
            <motion.div variants={itemVariants}>
              <Card>
                <h3 className="text-lg font-bold mb-4">📅 Upcoming Events</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {data.upcoming_events.map((event, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.05 * idx }}
                      className="p-3 rounded bg-white/5 text-sm border-l-2 border-brand-secondary"
                    >
                      <p className="font-semibold">{event.full_name}</p>
                      <p className="text-white/60 text-xs">{event.event_type}</p>
                      <p className="text-white/40 text-xs mt-1">{event.event_date}</p>
                    </motion.div>
                  ))}
                </div>
              </Card>
            </motion.div>
          )}
        </motion.div>
      )}
    </motion.div>
  )
}

export default Dashboard
