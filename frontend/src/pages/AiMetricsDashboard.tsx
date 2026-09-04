import { useQuery } from '@tanstack/react-query'
import { fetchAiMetrics } from '@/api/claims'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export function AiMetricsDashboard() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['ai-metrics'],
    queryFn: fetchAiMetrics,
    refetchInterval: 60_000,
  })

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-28" />)}
      </div>
    )
  }

  if (!metrics) return null

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold text-gray-900">AI Metrics</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500 font-medium">Analyzed</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-gray-900">{metrics.total_analyzed}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500 font-medium">Mismatch rate</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-amber-600">
              {(metrics.mismatch_rate * 100).toFixed(1)}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500 font-medium">Avg latency</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-gray-900">
              {metrics.avg_latency_ms != null ? `${Math.round(metrics.avg_latency_ms)}ms` : '—'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-gray-500 font-medium">Flagged</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-gray-900">{metrics.mismatch_count}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Provider breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          {Object.keys(metrics.provider_breakdown).length === 0 ? (
            <p className="text-sm text-gray-400">No data yet</p>
          ) : (
            <div className="space-y-2">
              {Object.entries(metrics.provider_breakdown).map(([provider, count]) => (
                <div key={provider} className="flex items-center justify-between">
                  <span className="text-sm font-medium capitalize">{provider}</span>
                  <span className="text-sm text-gray-500">{count} calls</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
