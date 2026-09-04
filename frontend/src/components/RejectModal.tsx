import { useState } from 'react'
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
}

export function RejectModal({ open, onClose, onConfirm, isLoading }: Props) {
  const [comment, setComment] = useState('')

  function handleConfirm() {
    if (!comment.trim()) return
    onConfirm(comment.trim())
  }

  function handleClose() {
    setComment('')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={(o) => !o && handleClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Reject claim</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <Label htmlFor="reject-comment">
              Reason for rejection <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="reject-comment"
              placeholder="Explain why this claim is being rejected…"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
              className="mt-1"
            />
          </div>
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
