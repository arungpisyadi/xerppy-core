import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bell, Search, User, ChevronDown, LogOut, Settings } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export function Header() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [isSearchOpen, setIsSearchOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const currentUser = user || {
    email: 'admin@xerppy.com',
    role: 'Administrator',
    name: 'Admin User',
  }

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-40 flex w-full bg-white drop-shadow-1 dark:bg-boxdark dark:drop-shadow-none border-b border-gray-200 dark:border-gray-800">
      <div className="flex flex-grow items-center justify-between px-4 py-4 shadow-2 md:px-6 2xl:px-11">
        <div className="flex items-center gap-4">
          {/* Hamburger Toggle */}
          <button
            className="z-99999 block rounded border border-gray-200 bg-white p-1.5 shadow-sm lg:hidden"
            onClick={() => setIsSearchOpen(!isSearchOpen)}
          >
            <svg className="fill-current" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 5H16M4 10H16M4 15H16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </button>

          {/* Search */}
          <div className={`${isSearchOpen ? 'block' : 'hidden'} lg:block`}>
            <div className="relative">
              <input
                type="text"
                placeholder="Type to search..."
                className="w-full bg-gray-50 py-2.5 pl-10 pr-4 text-sm text-gray-700 border border-gray-200 rounded-lg focus:outline-none focus:border-brand-500 dark:bg-gray-900 dark:text-gray-300 dark:border-gray-700"
              />
              <button className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400">
                <Search size={18} />
              </button>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 sm:gap-4">
          {/* Dark Mode Toggle */}
          <button className="hidden lg:flex items-center justify-center rounded-full bg-gray-100 p-2 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700">
            <svg className="fill-current" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 2C6.13401 2 3 5.13401 3 9C3 12.866 6.13401 16 10 16C10.4142 16 10.75 16.3358 10.75 16.75C10.75 17.1642 10.4142 17.5 10 17.5C5.58172 17.5 2 13.9183 2 9.5C2 5.08172 5.58172 1.5 10 1.5C13.9036 1.5 17.1804 4.21478 18.2548 7.92131C18.1803 7.69648 18.125 7.45655 18.125 7.20312C18.125 5.28053 19.6556 3.75 21.5781 3.75C23.5007 3.75 25.0312 5.28053 25.0312 7.20312C25.0312 7.91232 24.7434 8.56291 24.273 9.06416C24.3949 9.4938 24.4531 9.94561 24.4531 10.4062C24.4531 13.3675 22.082 15.7385 19.1207 15.7385C18.1772 15.7385 17.2829 15.4758 16.536 15.0237C16.3327 14.8841 16.0994 14.7969 15.8438 14.7969C15.4295 14.7969 15.0938 15.1327 15.0938 15.5469C15.0938 15.9611 15.4295 16.2969 15.8438 16.2969C16.9369 16.2969 17.9698 16.727 18.7656 17.4319C19.5615 18.1367 20.0781 19.0786 20.0781 20.125C20.0781 21.1714 19.5615 22.1133 18.7656 22.8181C17.9698 22.1133 16.9369 21.6832 15.8438 21.6832C15.4295 21.6832 15.0938 22.0189 15.0938 22.4332C15.0938 22.8474 15.4295 23.1832 15.8438 23.1832C17.7809 23.1832 19.5659 24.0419 20.8792 25.3552C22.1924 26.6685 23.0511 28.4535 23.0511 30.3906C23.0511 32.3277 22.1924 34.1127 20.8792 35.426C20.5374 35.7678 20.0781 36 19.5781 36H2.92188C2.42188 36 1.96251 35.7678 1.62071 35.426C0.307393 34.1127 -0.55127 32.3277 -0.55127 30.3906C-0.55127 29.2327 -0.0581813 28.127 0.825195 27.3291C0.496736 27.0364 0.230469 26.6818 0.0429688 26.2863C-0.144531 25.8908 -0.253906 25.4673 -0.253906 25.0312C-0.253906 24.5952 -0.144531 24.1717 0.0429688 23.7762C0.230469 23.3807 0.496736 23.0261 0.825195 22.7334C-0.0581818 21.9355 -0.55127 20.8298 -0.55127 19.6719C-0.55127 17.7348 0.307393 15.9498 1.62071 14.6365C2.93402 13.3232 4.71906 12.4645 6.65625 12.4645C7.81412 12.4645 8.91983 12.9576 9.71777 13.8409C10.0104 13.5125 10.365 13.2462 10.7605 13.0587C11.156 12.8712 11.5796 12.7618 12.0156 12.7618C12.4516 12.7618 12.8752 12.8712 13.2707 13.0587C13.6662 13.2462 14.0208 13.5125 14.3135 13.8409C14.7251 13.2729 15.2654 12.8203 15.8906 12.5237C16.5159 12.2271 17.1973 12.094 17.8906 12.1311C18.584 12.1683 19.2547 12.4635 19.8501 12.9924C20.4455 13.5213 20.9438 14.2679 21.306 15.1716C21.6682 16.0752 21.8812 17.1019 21.9203 18.1604C21.9595 19.2189 21.8226 20.2718 21.5203 21.2346C21.218 22.1973 20.7597 23.0501 20.1824 23.7324C19.605 24.4148 18.9226 24.9104 18.1843 25.1877C17.4461 25.465 16.6669 25.5174 15.9055 25.3411C15.1441 25.1648 14.4226 24.767 13.7942 24.1829C13.1659 23.5987 12.6477 22.8416 12.2761 21.9641C11.9045 21.0866 11.6903 20.1223 11.6466 19.1419C11.6029 18.1614 11.7303 17.1833 12.0198 16.2771C12.3093 15.3708 12.7526 14.5506 13.3225 13.8665C13.8923 13.1824 14.5765 12.6467 15.3344 12.2903C16.0923 11.9338 16.909 11.7631 17.7344 11.7893C18.5597 11.8154 19.3678 12.0379 20.1087 12.4426C20.8496 12.8474 21.5074 13.4256 22.0433 14.1448C22.5791 14.864 22.9808 15.7066 23.2225 16.6213C23.4641 17.536 23.5405 18.5041 23.4471 19.4658C23.3537 20.4276 22.9931 21.3599 22.3919 22.2049C21.7907 23.0498 21.0613 23.7908 20.2458 24.3848C19.4303 23.7908 18.7009 23.0498 18.0997 22.2049C17.4985 21.3599 17.1379 20.4276 17.0445 19.4658C16.9511 18.5041 17.0275 17.536 17.2691 16.6213C17.5108 15.7066 17.9125 14.864 18.4483 14.1448C18.9842 13.4256 19.642 12.8474 20.3829 12.4426C21.1238 12.0379 21.9319 11.8154 22.7572 11.7893C23.5826 11.7631 24.3993 11.9338 25.1572 12.2903C25.9151 12.6467 26.5993 13.1824 27.1692 13.8665C27.739 14.5506 28.1823 15.3708 28.4718 16.2771C28.7613 17.1833 28.8887 18.1614 28.845 19.1419C28.8013 20.1223 28.5871 21.0866 28.2155 21.9641C27.8439 22.8416 27.3257 23.5987 26.6974 24.1829C26.069 24.767 25.3475 25.1648 24.5861 25.3411C23.8247 25.5174 23.0455 25.465 22.3073 25.1877C21.569 24.9104 20.8866 24.4148 20.3092 23.7324C19.7319 23.0501 19.2736 22.1973 18.9713 21.2346C18.669 20.2718 18.5033 19.2189 18.5424 18.1604C18.5816 17.1019 18.7945 16.0752 19.1567 15.1716C19.5189 14.2679 20.0172 13.5213 20.6126 12.9924C21.208 12.4635 21.8786 12.1683 22.572 12.1311C23.2654 12.094 23.9467 12.2271 24.572 12.5237C25.1972 12.8203 25.7375 13.2729 26.1491 13.8409C26.4418 14.1694 26.7965 14.4356 27.192 14.6231C27.5874 14.8106 28.011 14.9199 28.447 14.9199C28.883 14.9199 29.3066 14.8106 29.702 14.6231C30.0975 14.4356 30.4521 14.1694 30.7448 13.8409C31.5427 12.9576 32.6485 12.4645 33.8064 12.4645C35.7435 12.4645 37.5286 13.3232 38.8419 14.6365C40.1552 15.9498 41.0139 17.7348 41.0139 19.6719C41.0139 21.6089 40.1552 23.394 38.8419 24.7073C38.5001 25.0491 38.0407 25.2812 37.5407 25.2812H37.1211C36.6211 25.2812 36.1617 25.0491 35.8199 24.7073C35.4781 24.3655 35.2461 23.9061 35.2461 23.4062C35.2461 22.9062 35.4781 22.4468 35.8199 22.105C36.8366 21.0884 37.6826 19.8967 38.3097 18.5837C38.9368 17.2708 39.3327 15.8562 39.4754 14.4163C39.6181 12.9764 39.5043 11.5297 39.1408 10.1536C38.7773 8.77758 38.171 7.49413 37.3576 6.36354C36.5442 5.23294 35.5351 4.27086 34.3785 3.52565C33.222 2.78043 31.9338 2.26327 30.5755 1.99939C29.2172 1.73551 27.8116 1.72936 26.4506 1.98116C25.0897 2.23296 23.7961 2.73826 22.6328 3.47206C22.3255 3.14358 21.9708 2.87732 21.5754 2.68982C21.18 2.50232 20.7564 2.39294 20.3244 2.39294C19.8924 2.39294 19.4688 2.50232 19.0734 2.68982C18.678 2.87732 18.3233 3.14358 18.016 3.47206C16.8528 2.73826 15.5591 2.23296 14.1982 1.98116C12.8373 1.72936 11.4317 1.73551 10.0733 1.99939C8.71502 2.26327 7.4268 2.78043 6.27026 3.52565C5.11371 4.27086 4.10461 5.23294 3.29121 6.36354C2.47781 7.49413 1.87146 8.77758 1.50797 10.1536C1.14449 11.5297 1.03063 12.9764 1.17334 14.4163C1.31605 15.8562 1.71198 17.2708 2.33907 18.5837C2.96617 19.8967 3.81218 21.0884 4.82884 22.105C5.16903 22.4468 5.40039 22.9062 5.40039 23.4062C5.40039 23.9062 5.16903 24.3655 4.82884 24.7073C4.48704 25.0491 4.02767 25.2812 3.52767 25.2812C3.02767 25.2812 2.5683 25.0491 2.2265 24.7073C0.913188 23.394 0.0545044 21.6089 0.0545044 19.6719C0.0545044 18.1224 0.624704 16.626 1.65625 15.4512" fill="#98A2B3"/>
            </svg>
          </button>

          {/* Notifications */}
          <button className="relative flex items-center justify-center rounded-full bg-gray-100 p-2 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700">
            <Bell size={20} />
            <span className="absolute top-0 right-0 z-1 h-2.5 w-2.5 rounded-full bg-red-500">
              <span className="absolute -z-1 inline-flex h-full w-full animate-ping rounded-full bg-red-500 opacity-75"></span>
            </span>
          </button>

          {/* User Menu */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-3 rounded-lg bg-gray-100 px-3 py-2 dark:bg-gray-800"
            >
              <div className="h-8 w-8 rounded-full bg-brand-500 flex items-center justify-center">
                <User className="h-4 w-4 text-white" />
              </div>
              <div className="hidden text-left lg:block">
                <span className="block text-sm font-medium text-gray-700 dark:text-white">
                  {currentUser.name}
                </span>
                <span className="block text-xs text-gray-500 dark:text-gray-400">
                  {currentUser.role}
                </span>
              </div>
              <ChevronDown className="hidden h-4 w-4 text-gray-500 dark:text-gray-400 lg:block" />
            </button>

            {/* Dropdown */}
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-800 dark:bg-gray-900">
                <div className="border-b border-gray-100 px-4 py-3 dark:border-gray-800">
                  <p className="text-sm font-medium text-gray-700 dark:text-white">
                    {currentUser.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {currentUser.email}
                  </p>
                </div>
                <div className="py-1">
                  <button 
                    onClick={() => navigate('/settings')}
                    className="flex w-full items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                  >
                    <Settings size={16} />
                    Settings
                  </button>
                  <button 
                    onClick={handleLogout}
                    className="flex w-full items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                  >
                    <LogOut size={16} />
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
