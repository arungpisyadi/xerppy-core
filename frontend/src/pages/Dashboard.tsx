import { TrendingUp, Users, Package, DollarSign, ArrowUpRight, ArrowDownRight } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string
  change: string
  isPositive: boolean
  icon: React.ComponentType<{ className?: string }>
}

function StatCard({ title, value, change, isPositive, icon: Icon }: StatCardProps) {
  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500 font-medium">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
          <Icon className="w-6 h-6 text-primary-600" />
        </div>
      </div>
      <div className="flex items-center gap-1 mt-4">
        {isPositive ? (
          <ArrowUpRight className="w-4 h-4 text-green-500" />
        ) : (
          <ArrowDownRight className="w-4 h-4 text-red-500" />
        )}
        <span className={`text-sm font-medium ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
          {change}
        </span>
        <span className="text-sm text-gray-500">vs last month</span>
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
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Welcome back! Here's what's happening with your business.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <StatCard key={stat.title} {...stat} />
        ))}
      </div>

      {/* Recent Activity Section */}
      <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-primary-50 rounded-full flex items-center justify-center">
                  <Package className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">New order #{1000 + i}</p>
                  <p className="text-xs text-gray-500">Customer: John Doe</p>
                </div>
              </div>
              <span className="text-sm font-medium text-gray-900">${(Math.random() * 500).toFixed(2)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
