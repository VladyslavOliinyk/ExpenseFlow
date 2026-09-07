import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Sparkles, Loader2 } from 'lucide-react'
import { fetchCategories } from '@/api/categories'
import { createClaim, suggestCategory } from '@/api/claims'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { Category } from '@/types'

interface Suggestion {
  category: string | null
  confidence: string | null
  loading: boolean
}

type FormFields = 'category_id' | 'amount' | 'description' | 'expense_date' | 'payment_details'
type Errors = Partial<Record<FormFields, string>>

const TODAY = new Date().toISOString().split('T')[0]

function validate(form: Record<FormFields, string>): Errors {
  const errs: Errors = {}
  if (!form.category_id) errs.category_id = 'Required'
  if (!form.amount || Number(form.amount) <= 0) errs.amount = 'Amount must be greater than 0'
  if (!form.description.trim()) errs.description = 'Required'
  if (!form.expense_date) {
    errs.expense_date = 'Required'
  } else if (form.expense_date > TODAY) {
    errs.expense_date = 'Expense date cannot be in the future'
  }
  if (!form.payment_details.trim()) {
    errs.payment_details = 'Required'
  } else if (form.payment_details.length > 200) {
    errs.payment_details = 'Maximum 200 characters'
  }
  return errs
}

export function NewClaimPage() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [form, setForm] = useState<Record<FormFields, string>>({
    category_id: '',
    amount: '',
    description: '',
    expense_date: '',
    payment_details: '',
  })
  const [errors, setErrors] = useState<Errors>({})
  const [shaking, setShaking] = useState(false)
  const [suggestion, setSuggestion] = useState<Suggestion | null>(null)

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories,
  })

  // Debounced category suggestion — fires 800ms after the user stops typing
  useEffect(() => {
    if (form.description.trim().length < 10) {
      setSuggestion(null)
      return
    }

    let cancelled = false

    const timer = setTimeout(() => {
      setSuggestion({ category: null, confidence: null, loading: true })
      suggestCategory(form.description)
        .then((result) => {
          if (!cancelled) {
            setSuggestion({
              category: result.suggested_category,
              confidence: result.confidence,
              loading: false,
            })
          }
        })
        .catch(() => {
          if (!cancelled) setSuggestion(null)
        })
    }, 800)

    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [form.description])

  function setField(field: FormFields, value: string) {
    setForm((f) => ({ ...f, [field]: value }))
    if (errors[field]) setErrors((e) => ({ ...e, [field]: undefined }))
  }

  function applySuggestion(categoryName: string) {
    const match = categories.find((c: Category) => c.name === categoryName)
    if (match) setField('category_id', String(match.id))
  }

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

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const errs = validate(form)
    if (Object.keys(errs).length > 0) {
      setErrors(errs)
      setShaking(true)
      setTimeout(() => setShaking(false), 400)
      return
    }
    setErrors({})
    mutation.mutate()
  }

  const err = (field: FormFields) => errors[field]
  const fieldClass = (field: FormFields) =>
    err(field) ? 'border-red-500 focus-visible:ring-red-500' : ''

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>New expense claim</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className={`space-y-4 ${shaking ? 'animate-shake' : ''}`}>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label>Category *</Label>
                <Select
                  value={form.category_id}
                  onValueChange={(v) => setField('category_id', v)}
                >
                  <SelectTrigger className={err('category_id') ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((c: Category) => (
                      <SelectItem key={c.id} value={String(c.id)}>
                        {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {err('category_id') && (
                  <p className="text-xs text-red-500">{err('category_id')}</p>
                )}

                {/* AI category suggestion */}
                {suggestion?.loading && (
                  <div className="flex items-center gap-1 text-xs text-gray-400 mt-1">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    Suggesting…
                  </div>
                )}
                {!suggestion?.loading && suggestion?.category && (
                  <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                    <Sparkles className="h-3 w-3 text-blue-400 shrink-0" />
                    <span className="text-xs text-gray-500">AI suggests:</span>
                    <button
                      type="button"
                      onClick={() => applySuggestion(suggestion.category!)}
                      className="text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded px-2 py-0.5 hover:bg-blue-100 transition-colors"
                    >
                      {suggestion.category}
                      {suggestion.confidence === 'high' && ' ✓'}
                    </button>
                  </div>
                )}
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
                  className={fieldClass('amount')}
                  onChange={(e) => setField('amount', e.target.value)}
                />
                {err('amount') && (
                  <p className="text-xs text-red-500">{err('amount')}</p>
                )}
              </div>
            </div>

            <div className="space-y-1">
              <Label htmlFor="expense_date">Expense date *</Label>
              <Input
                id="expense_date"
                type="date"
                max={TODAY}
                value={form.expense_date}
                className={fieldClass('expense_date')}
                onChange={(e) => setField('expense_date', e.target.value)}
              />
              {err('expense_date') && (
                <p className="text-xs text-red-500">{err('expense_date')}</p>
              )}
            </div>

            <div className="space-y-1">
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                placeholder="What was this expense for?"
                rows={3}
                value={form.description}
                className={fieldClass('description')}
                onChange={(e) => setField('description', e.target.value)}
              />
              {err('description') && (
                <p className="text-xs text-red-500">{err('description')}</p>
              )}
            </div>

            <div className="space-y-1">
              <Label htmlFor="payment_details">Payment details *</Label>
              <Textarea
                id="payment_details"
                placeholder="Bank account, PayPal, or other reimbursement details"
                rows={2}
                maxLength={200}
                value={form.payment_details}
                className={fieldClass('payment_details')}
                onChange={(e) => setField('payment_details', e.target.value)}
              />
              {err('payment_details') && (
                <p className="text-xs text-red-500">{err('payment_details')}</p>
              )}
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
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? 'Submitting…' : 'Submit claim'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
