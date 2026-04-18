import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../hooks/useAuth'

const Topbar = ({ title = 'AI Mail Assistant' }) => {
  const { user } = useAuth()

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed top-0 right-0 left-0 z-50 glass m-4 md:ml-80 md:mr-4"
    >
      <div className="max-w-full mx-auto px-6 py-4 flex items-center justify-between">
        <h2 className="text-xl font-bold gradient-text">{title}</h2>
        <div className="flex items-center gap-6">
          <span className="text-sm text-white/60">{user?.username || 'User'}</span>
          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-brand-primary to-brand-secondary flex items-center justify-center text-white font-bold">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
        </div>
      </div>
    </motion.header>
  )
}

export default Topbar
