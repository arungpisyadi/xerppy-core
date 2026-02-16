import { TrendingUp, Users, Package, DollarSign, ArrowUpRight, ArrowDownRight } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string
  change: string
  isPositive: boolean
  icon: React.ComponentType<{ className?: string; size?: number }>
}

function StatCard({ title, value, change, isPositive, icon: Icon }: StatCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <p className="mt-1 text-2xl font-bold text-gray-800 dark:text-white">{value}</p>
        </div>
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-500/10">
          <Icon className="h-6 w-6 text-brand-600 dark:text-brand-500" size={24} />
        </div>
      </div>
      <div className="mt-4 flex items-center gap-1">
        {isPositive ? (
          <ArrowUpRight className="h-4 w-4 text-green-500" size={16} />
        ) : (
          <ArrowDownRight className="h-4 w-4 text-red-500" size={16} />
        )}
        <span className={`text-sm font-medium ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
          {change}
        </span>
        <span className="text-sm text-gray-500 dark:text-gray-400">vs last month</span>
      </div>
    </div>
  )
}

export function Dashboard() {
  const stats = [
    { title: 'Total Revenue', value: '$54,230', change: '+12.5%', isPositive: true, icon: DollarSign },
    { title: 'Total Customers', value: '1,234', change: '+8.2%', isPositive: true, icon: Users },
    { title: 'Total Products', value: '856', change: '+3.1%', isPositive: true, icon: Package },
    { title: 'Growth Rate', value: '24.5%', change: '-2.4%', isPositive: false, icon: TrendingUp },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-800 dark:text-white/90">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Welcome back! Here's what's happening with your business.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4 lg:gap-6">
        {stats.map((stat) => (
          <StatCard key={stat.title} {...stat} />
        ))}
      </div>

      {/* Recent Activity Section */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
        <h2 className="mb-4 text-lg font-semibold text-gray-800 dark:text-white/90">Recent Activity</h2>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="flex items-center justify-between border-b border-gray-100 py-3 last:border-0 dark:border-gray-800"
            >
              <div className="flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-500/10">
                  <Package className="h-5 w-5 text-brand-600 dark:text-brand-500" size={20} />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800 dark:text-white">New order #{1000 + i}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Customer: John Doe</p>
                </div>
              </div>
              <span className="text-sm font-medium text-gray-800 dark:text-white">
                ${(Math.random() * 500).toFixed(2)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
