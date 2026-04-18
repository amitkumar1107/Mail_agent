import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../hooks/useAuth'

const Sidebar = ({ open = true }) => {
  const location = useLocation()
  const { logout } = useAuth()
  const isActive = (path) => location.pathname === path

  const menuItems = [
    { label: 'Dashboard', icon: '📊', path: '/dashboard' },
    { label: 'Chat Assistant', icon: '💬', path: '/chat' },
    { label: 'Contacts', icon: '👥', path: '/contacts' },
    { label: 'Reminders', icon: '🔔', path: '/reminders' },
    { label: 'Templates', icon: '📝', path: '/templates' },
    { label: 'History', icon: '📜', path: '/history' },
  ]

  const containerVariants = {
    open: { x: 0, opacity: 1 },
    closed: { x: -288, opacity: 0 },
  }

  return (
    <motion.aside
      variants={containerVariants}
      initial="open"
      animate={open ? 'open' : 'closed'}
      className="w-72 bg-white/5 border-r border-white/10 p-6 backdrop-blur-md h-screen fixed left-0 top-0 z-40 pt-24 overflow-y-auto"
    >
      <div className="mb-8">
        <h1 className="gradient-text text-2xl font-bold">AI Mail</h1>
        <p className="text-white/50 text-sm mt-1">Assistant Pro</p>
      </div>

      <nav className="space-y-2">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`block px-4 py-3 rounded-lg transition-smooth ${
              isActive(item.path)
                ? 'bg-brand-primary/20 text-brand-secondary border-l-4 border-brand-primary'
                : 'text-white/70 hover:bg-white/10'
            }`}
          >
            <span className="text-xl mr-3">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="mt-auto pt-6 border-t border-white/10">
        <button
          onClick={logout}
          className="w-full px-4 py-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20 transition-smooth text-sm font-medium"
        >
          Logout
        </button>
      </div>
    </motion.aside>
  )
}

export default Sidebar
