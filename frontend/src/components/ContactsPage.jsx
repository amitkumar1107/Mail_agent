import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { contactsService } from '../services/api'
import { Card, Button, Input } from './UI'

const ContactsPage = () => {
  const [contacts, setContacts] = useState([])
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    relationship: 'other',
  })

  useEffect(() => {
    loadContacts()
  }, [])

  const loadContacts = async () => {
    setLoading(true)
    try {
      const response = await contactsService.getContacts()
      setContacts(response.data.results || response.data || [])
    } catch (error) {
      console.error('Failed to load contacts:', error)
    }
    setLoading(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await contactsService.createContact(formData)
      setFormData({ full_name: '', email: '', phone: '', relationship: 'other' })
      await loadContacts()
    } catch (error) {
      alert('Failed to create contact')
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Form */}
      <Card className="lg:col-span-1">
        <h3 className="text-lg font-bold mb-4">Add Contact</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Full Name"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            required
          />
          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
          <Input
            label="Phone"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          />
          <div>
            <label className="block text-sm font-medium mb-2">Relationship</label>
            <select
              value={formData.relationship}
              onChange={(e) => setFormData({ ...formData, relationship: e.target.value })}
              className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg focus:outline-none focus:border-brand-primary text-white"
            >
              <option value="other">Other</option>
              <option value="family">Family</option>
              <option value="friend">Friend</option>
              <option value="work">Work</option>
            </select>
          </div>
          <Button variant="primary" className="w-full">
            Add Contact
          </Button>
        </form>
      </Card>

      {/* Contacts List */}
      <div className="lg:col-span-2 space-y-3">
        <h3 className="text-lg font-bold mb-4">Your Contacts ({contacts.length})</h3>
        {contacts.length === 0 ? (
          <Card className="text-center py-8">
            <p className="text-white/60">No contacts yet. Add one to get started!</p>
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
            {contacts.map((contact, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="glass p-4"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold text-brand-secondary">{contact.full_name}</p>
                    <p className="text-sm text-white/60">{contact.email}</p>
                    {contact.phone && (
                      <p className="text-sm text-white/50">{contact.phone}</p>
                    )}
                  </div>
                  <span className="text-xs bg-brand-primary/20 text-brand-primary px-2 py-1 rounded">
                    {contact.relationship}
                  </span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default ContactsPage
