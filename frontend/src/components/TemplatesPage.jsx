import React from 'react'
import { motion } from 'framer-motion'
import { Card } from './UI'

const TemplatesPage = () => {
  const templates = [
    {
      id: 1,
      name: 'Follow Up',
      description: 'Professional follow-up email template',
      icon: '📧',
    },
    {
      id: 2,
      name: 'Thank You',
      description: 'Gratitude and thank you emails',
      icon: '🙏',
    },
    {
      id: 3,
      name: 'Apology',
      description: 'Professional apology emails',
      icon: '😔',
    },
    {
      id: 4,
      name: 'Introduction',
      description: 'Self-introduction templates',
      icon: '👋',
    },
  ]

  return (
    <div>
      <h3 className="text-lg font-bold mb-6">Email Templates</h3>
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
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
        {templates.map((template) => (
          <motion.div
            key={template.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ y: -5 }}
          >
            <Card className="cursor-pointer hover-lift h-full">
              <div className="text-4xl mb-3">{template.icon}</div>
              <h4 className="font-bold mb-1">{template.name}</h4>
              <p className="text-sm text-white/60">{template.description}</p>
              <button className="mt-4 w-full px-3 py-2 rounded bg-brand-primary/20 text-brand-primary text-sm font-medium hover:bg-brand-primary/30 transition-smooth">
                Use Template
              </button>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}

export default TemplatesPage
