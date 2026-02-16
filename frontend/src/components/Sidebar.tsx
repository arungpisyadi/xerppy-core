import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Settings, 
  Package, 
  Users, 
  BarChart3, 
  FileText,
  ChevronDown,
  LogOut
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

interface NavItem {
  to: string
  icon: React.ComponentType<{ className?: string; size?: number }>
  label: string
  children?: NavItem[]
}

const menuItems: NavItem[] = [
  { 
    to: '/dashboard', 
    icon: LayoutDashboard, 
    label: 'Dashboard' 
  },
  { 
    to: '/settings', 
    icon: Settings, 
    label: 'Settings' 
  },
]

const navItems: NavItem[] = [
  { to: '/products', icon: Package, label: 'Products' },
  { to: '/customers', icon: Users, label: 'Customers' },
  { to: '/reports', icon: BarChart3, label: 'Reports' },
  { to: '/invoices', icon: FileText, label: 'Invoices' },
]

export function Sidebar() {
  const [selected, setSelected] = useState<string>('Dashboard')
  const [isCollapsed, setIsCollapsed] = useState(false)
  const { logout } = useAuth()

  const handleLogout = async () => {
    await logout()
  }

  return (
    <aside
      className={`sidebar ${isCollapsed ? 'lg:w-[90px]' : ''}`}
    >
      {/* SIDEBAR HEADER */}
      <div className={`sidebar-header ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
        <NavLink to="/dashboard" className="flex items-center gap-2">
          <span className={`logo ${isCollapsed ? 'hidden' : ''}`}>
            {/* Logo Icon */}
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="32" height="32" rx="8" fill="#3B82F6"/>
              <path d="M9 16L16 9L23 16L16 23L9 16Z" fill="white" stroke="white" strokeWidth="1.5" strokeLinejoin="round"/>
            </svg>
          </span>
          <svg
            className={`logo-icon ${isCollapsed ? 'lg:block' : 'hidden'}`}
            width="32"
            height="32"
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect width="32" height="32" rx="8" fill="#3B82F6"/>
            <path d="M9 16L16 9L23 16L16 23L9 16Z" fill="white" stroke="white" strokeWidth="1.5" strokeLinejoin="round"/>
          </svg>
          {!isCollapsed && (
            <span className="text-lg font-bold text-gray-800 dark:text-white">
              Xerppy
            </span>
          )}
        </NavLink>

        {/* Toggle Button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="lg:hidden p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-white"
        >
          <svg className="fill-current" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 5H16M4 10H16M4 15H16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </button>
      </div>

      {/* Scrollable Content */}
      <div className="no-scrollbar flex flex-col overflow-y-auto duration-300 ease-linear">
        {/* Menu Group */}
        <div>
          <h3 className="mb-4 text-xs uppercase leading-[20px] text-gray-400">
            <span className={`menu-group-title ${isCollapsed ? 'lg:hidden' : ''}`}>
              MENU
            </span>
            <svg
              className={`menu-group-icon mx-auto fill-current ${isCollapsed ? 'lg:block hidden' : 'hidden'}`}
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path fillRule="evenodd" clipRule="evenodd" d="M5.99915 10.2451C6.96564 10.2451 7.74915 11.0286 7.74915 11.9951V12.0051C7.74915 12.9716 6.96564 13.7551 5.99915 13.7551C5.03265 13.7551 4.24915 12.9716 4.24915 12.0051V11.9951C4.24915 11.0286 5.03265 10.2451 5.99915 10.2451ZM17.9991 10.2451C18.9656 10.2451 19.7491 11.0286 19.7491 11.9951V12.0051C19.7491 12.9716 18.9656 13.7551 17.9991 13.7551C17.0326 13.7551 16.2491 12.9716 16.2491 12.0051V11.9951C16.2491 11.0286 17.0326 10.2451 17.9991 10.2451ZM13.7491 11.9951C13.7491 11.0286 12.9656 10.2451 11.9991 10.2451C11.0326 10.2451 10.2491 11.0286 10.2491 11.9951V12.0051C10.2491 12.9716 11.0326 13.7551 11.9991 13.7551C12.9656 13.7551 13.7491 12.9716 13.7491 12.0051V11.9951Z" fill=""/>
            </svg>
          </h3>

          <ul className="mb-6 flex flex-col gap-4">
            {/* Menu Items */}
            {menuItems.map((item) => {
              const Icon = item.icon
              return (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    className={({ isActive }) =>
                      `menu-item group ${isActive ? 'menu-item-active' : 'menu-item-inactive'}`
                    }
                  >
                    <Icon
                      className={selected === item.label ? 'text-brand-500' : 'text-gray-500 dark:text-gray-400'}
                      size={24}
                    />
                    <span className={`menu-item-text ${isCollapsed ? 'lg:hidden' : ''}`}>
                      {item.label}
                    </span>
                  </NavLink>
                </li>
              )
            })}

            {/* Expandable Menu Item */}
            <li>
              <button
                onClick={() => setSelected(selected === 'Management' ? '' : 'Management')}
                className={`menu-item group w-full ${selected === 'Management' ? 'menu-item-active' : 'menu-item-inactive'}`}
              >
                <Users
                  className={selected === 'Management' ? 'text-brand-500' : 'text-gray-500 dark:text-gray-400'}
                  size={24}
                />
                <span className={`menu-item-text ${isCollapsed ? 'lg:hidden' : ''}`}>
                  Management
                </span>
                <ChevronDown
                  className={`menu-item-arrow ${selected === 'Management' ? 'rotate-180' : ''} ${isCollapsed ? 'lg:hidden' : ''}`}
                  size={20}
                />
              </button>

              {/* Dropdown */}
              <div
                className={`transform overflow-hidden ${selected === 'Management' ? 'block' : 'hidden'}`}
              >
                <ul className={`menu-dropdown mt-2 flex flex-col gap-1 ${isCollapsed ? 'lg:hidden' : 'flex'}`}>
                  {navItems.map((item) => {
                    const Icon = item.icon
                    return (
                      <li key={item.to}>
                        <NavLink
                          to={item.to}
                          className={({ isActive }) =>
                            `menu-dropdown-item group ${isActive ? 'menu-dropdown-item-active' : 'menu-dropdown-item-inactive'}`
                          }
                        >
                          <Icon size={18} className="mr-2" />
                          {item.label}
                        </NavLink>
                      </li>
                    )
                  })}
                </ul>
              </div>
            </li>
          </ul>
        </div>
      </div>

      {/* Logout Button */}
      <div className="border-t border-gray-200 dark:border-gray-800 pt-4 mt-auto">
        <button
          onClick={handleLogout}
          className={`menu-item w-full text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300`}
        >
          <LogOut size={24} />
          <span className={`${isCollapsed ? 'lg:hidden' : ''}`}>Logout</span>
        </button>
      </div>
    </aside>
  )
}
