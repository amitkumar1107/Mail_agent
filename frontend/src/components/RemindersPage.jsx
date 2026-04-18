import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { remindersService } from '../services/api'
import { Card, Button, Input } from './UI'

const RemindersPage = () => {
  const [reminders, setReminders] = useState([])
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    contact: '',
    reminder_type: 'birthday',
    reminder_date: '',
  })

  useEffect(() => {
    loadReminders()
  }, [])

  const loadReminders = async () => {
    setLoading(true)
    try {
      const response = await remindersService.getReminders()
      setReminders(response.data.results || response.data || [])
    } catch (error) {
      console.error('Failed to load reminders:', error)
    }
    setLoading(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await remindersService.createReminder(formData)
      setFormData({ contact: '', reminder_type: 'birthday', reminder_date: '' })
      await loadReminders()
    } catch (error) {
      alert('Failed to create reminder')
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Form */}
      <Card className="lg:col-span-1">
        <h3 className="text-lg font-bold mb-4">Create Reminder</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Contact Name"
            value={formData.contact}
            onChange={(e) => setFormData({ ...formData, contact: e.target.value })}
            required
          />
          <div>
            <label className="block text-sm font-medium mb-2">Type</label>
            <select
              value={formData.reminder_type}
              onChange={(e) => setFormData({ ...formData, reminder_type: e.target.value })}
              className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg focus:outline-none focus:border-brand-primary text-white"
            >
              <option value="birthday">Birthday</option>
              <option value="anniversary">Anniversary</option>
              <option value="followup">Follow Up</option>
              <option value="other">Other</option>
            </select>
          </div>
          <Input
            label="Date"
            type="date"
            value={formData.reminder_date}
            onChange={(e) => setFormData({ ...formData, reminder_date: e.target.value })}
            required
          />
          <Button variant="primary" className="w-full">
            Create Reminder
          </Button>
        </form>
      </Card>

      {/* Reminders List */}
      <div className="lg:col-span-2 space-y-3">
        <h3 className="text-lg font-bold mb-4">Your Reminders ({reminders.length})</h3>
        {reminders.length === 0 ? (
          <Card className="text-center py-8">
            <p className="text-white/60">No reminders yet. Create one to stay organized!</p>
          </Card>
        ) : (
          <motion.div
            className="space-y-3 max-h-96 overflow-y-auto"
            initial="hidden"
            animate="show"
            variants={{
              show: {
                transition: {
                  staggerChildren: 0.05,
                },
              },
            }}
          >
            {reminders.map((reminder, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="glass p-4 border-l-4 border-brand-secondary"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold flex items-center gap-2">
                      <span>
                        {reminder.reminder_type === 'birthday'
                          ? '🎂'
                          : reminder.reminder_type === 'anniversary'
                          ? '💍'
                          : '📌'}
                      </span>
                      {reminder.contact}
                    </p>
                    <p className="text-sm text-white/60 mt-1">{reminder.reminder_type}</p>
                    <p className="text-xs text-white/40 mt-1">{reminder.reminder_date}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default RemindersPage
