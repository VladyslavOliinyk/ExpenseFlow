import { useState, useEffect } from 'react'
import { Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from '@/components/ui/dialog'

interface Props {
  open: boolean
  onClose: () => void
  onConfirm: (comment: string) => void
  isLoading?: boolean
  aiReason?: string
  error?: string
}

export function RejectModal({ open, onClose, onConfirm, isLoading, aiReason, error }: Props) {
  const [comment, setComment] = useState('')

  // Always start with an empty textarea when the modal opens
  useEffect(() => {
    if (open) setComment('')
  }, [open])

  function handleConfirm() {
    if (!comment.trim()) return
    onConfirm(comment.trim())
  }

  function handleClose() {
    setComment('')
    onClose()
  }

  function applyAiReason() {
    if (aiReason) setComment(aiReason)
  }

  return (
    <Dialog open={open} onOpenChange={(o) => !o && handleClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Reject claim</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between mb-1">
              <Label htmlFor="reject-comment">
                Reason for rejection <span className="text-red-500">*</span>
              </Label>
              {aiReason && (
                <button
                  type="button"
                  onClick={applyAiReason}
                  className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <Sparkles className="h-3 w-3" />
                  Use AI's reason
                </button>
              )}
            </div>
            <Textarea
              id="reject-comment"
              placeholder="Explain why this claim is being rejected…"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
            />
          </div>
          {error && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
              {error}
            </p>
          )}
          <div className="flex justify-end gap-2">
            <DialogClose asChild>
              <Button variant="outline" onClick={handleClose} disabled={isLoading}>
                Cancel
              </Button>
            </DialogClose>
            <Button
              variant="destructive"
              onClick={handleConfirm}
              disabled={!comment.trim() || isLoading}
            >
              {isLoading ? 'Rejecting…' : 'Reject'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
