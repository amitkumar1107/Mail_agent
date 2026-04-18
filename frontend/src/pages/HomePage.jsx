import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import Topbar from '../components/Topbar'
import Sidebar from '../components/Sidebar'
import ChatBox from '../components/ChatBox'
import Dashboard from '../components/Dashboard'
import ContactsPage from '../components/ContactsPage'
import RemindersPage from '../components/RemindersPage'
import TemplatesPage from '../components/TemplatesPage'
import HistoryPage from '../components/HistoryPage'
import { mailService } from '../services/api'

const HomePage = () => {
  const [currentPage, setCurrentPage] = useState('chat')
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(false)

  // Load dashboard data when component mounts or page changes to dashboard
  useEffect(() => {
    if (currentPage === 'dashboard') {
      loadDashboardData()
    }
  }, [currentPage])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      const response = await mailService.getDashboard()
      setDashboardData(response.data)
    } catch (error) {
      console.error('Failed to load dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const pageData = {
    chat: { title: '💬 Chat Assistant', component: <ChatBox /> },
    dashboard: { title: '📊 Dashboard', component: <Dashboard data={dashboardData} /> },
    contacts: { title: '👥 Contacts', component: <ContactsPage /> },
    reminders: { title: '🔔 Reminders', component: <RemindersPage /> },
    templates: { title: '📝 Templates', component: <TemplatesPage /> },
    history: { title: '📜 History', component: <HistoryPage /> },
  }

  const currentPageData = pageData[currentPage] || pageData.chat

  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-blue-900 to-purple-900">
      <Sidebar open={true} />
      <Topbar title={currentPageData.title} />

      {/* Main Content */}
      <main className="md:ml-72 pt-24 pb-6 px-4 md:px-8">
        <motion.div
          key={currentPage}
          variants={pageVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          transition={{ duration: 0.3 }}
          className={currentPage === 'chat' ? 'h-[calc(100vh-120px)]' : ''}
        >
          {currentPage === 'chat' ? (
            <div className="h-full glass rounded-2xl overflow-hidden">
              {currentPageData.component}
            </div>
          ) : (
            <div className="max-w-full">
              {currentPageData.component}
            </div>
          )}
        </motion.div>
      </main>

      {/* Mobile Bottom Navigation */}
      <motion.nav
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="fixed bottom-0 left-0 right-0 md:hidden glass border-t border-white/10 px-4 py-3"
      >
        <div className="flex justify-around items-center">
          {[
            { id: 'chat', icon: '💬', label: 'Chat' },
            { id: 'dashboard', icon: '📊', label: 'Dashboard' },
            { id: 'contacts', icon: '👥', label: 'Contacts' },
            { id: 'templates', icon: '📝', label: 'Templates' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`flex flex-col items-center gap-1 py-2 px-3 rounded-lg transition-smooth ${
                currentPage === item.id
                  ? 'bg-brand-primary/20 text-brand-secondary'
                  : 'text-white/60 hover:text-white'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="text-xs font-semibold">{item.label}</span>
            </button>
          ))}
        </div>
      </motion.nav>

      {/* Quick Page Switcher (Desktop) */}
      <style jsx>{`
        /* Hide default scrollbar on chat box, show custom */
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  )
}

export default HomePage
