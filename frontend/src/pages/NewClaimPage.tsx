import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchCategories } from '@/api/categories'
import { createClaim } from '@/api/claims'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function NewClaimPage() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [form, setForm] = useState({
    category_id: '',
    amount: '',
    description: '',
    expense_date: '',
    payment_details: '',
  })

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories,
  })

  const mutation = useMutation({
    mutationFn: () =>
      createClaim({
        category_id: Number(form.category_id),
        amount: form.amount,
        description: form.description,
        expense_date: form.expense_date,
        payment_details: form.payment_details,
      }),
    onSuccess: (claim) => {
      qc.invalidateQueries({ queryKey: ['claims'] })
      navigate(`/claims/${claim.id}`)
    },
  })

  const isValid =
    form.category_id && form.amount && form.description.trim() && form.expense_date && form.payment_details.trim()

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!isValid) return
    mutation.mutate()
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>New expense claim</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label>Category *</Label>
                <Select
                  value={form.category_id}
                  onValueChange={(v) => setForm((f) => ({ ...f, category_id: v }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((c) => (
                      <SelectItem key={c.id} value={String(c.id)}>
                        {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <Label htmlFor="amount">Amount (USD) *</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  min="0.01"
                  placeholder="0.00"
                  value={form.amount}
                  onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
                />
              </div>
            </div>

            <div className="space-y-1">
              <Label htmlFor="expense_date">Expense date *</Label>
              <Input
                id="expense_date"
                type="date"
                max={new Date().toISOString().split('T')[0]}
                value={form.expense_date}
                onChange={(e) => setForm((f) => ({ ...f, expense_date: e.target.value }))}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                placeholder="What was this expense for?"
                rows={3}
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="payment_details">Payment details *</Label>
              <Textarea
                id="payment_details"
                placeholder="Bank account, PayPal, or other reimbursement details"
                rows={2}
                maxLength={200}
                value={form.payment_details}
                onChange={(e) => setForm((f) => ({ ...f, payment_details: e.target.value }))}
              />
            </div>

            {mutation.isError && (
              <p className="text-sm text-red-500">
                Failed to submit. Please check all fields and try again.
              </p>
            )}

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => navigate('/claims')}>
                Cancel
              </Button>
              <Button type="submit" disabled={!isValid || mutation.isPending}>
                {mutation.isPending ? 'Submitting…' : 'Submit claim'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
