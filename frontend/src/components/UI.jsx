import React from 'react'
import { motion } from 'framer-motion'

export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  className = '', 
  ...props 
}) => {
  const baseStyles = 'font-semibold rounded-lg transition-smooth focus:outline-none flex items-center justify-center gap-2'
  
  const variants = {
    primary: 'bg-gradient-to-r from-brand-primary to-brand-secondary hover:shadow-lg hover:shadow-brand-primary/50',
    secondary: 'bg-white/10 hover:bg-white/20 border border-white/20 hover:border-white/40',
    outline: 'border-2 border-brand-primary text-brand-primary hover:bg-brand-primary/10',
    ghost: 'hover:bg-white/10',
    danger: 'bg-red-500/80 hover:bg-red-600',
  }

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-2.5 text-base',
    lg: 'px-8 py-3 text-lg',
  }

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  )
}

export const Card = ({ children, className = '', ...props }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className={`glass p-6 ${className}`}
    {...props}
  >
    {children}
  </motion.div>
)

export const Input = ({ label, error, className = '', ...props }) => (
  <div className={className}>
    {label && (
      <label className="block text-sm font-medium mb-2 text-white/80">
        {label}
      </label>
    )}
    <input
      className={`w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg focus:outline-none focus:border-brand-primary focus:ring-2 focus:ring-brand-primary/30 transition-smooth text-white placeholder-white/40`}
      {...props}
    />
    {error && (
      <p className="text-red-400 text-sm mt-1">{error}</p>
    )}
  </div>
)

export const Badge = ({ children, variant = 'primary', className = '' }) => {
  const variants = {
    primary: 'bg-brand-primary/20 text-brand-primary',
    success: 'bg-green-500/20 text-green-400',
    warning: 'bg-yellow-500/20 text-yellow-400',
    danger: 'bg-red-500/20 text-red-400',
  }

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${variants[variant]} ${className}`}>
      {children}
    </span>
  )
}
