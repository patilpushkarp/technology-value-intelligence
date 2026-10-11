/**
 * Reactive cursor state management for Maria João Abrantes inspired interactive pill cursor
 */

export interface CursorState {
  label: string
  isActive: boolean
  variant: 'default' | 'pill' | 'highlight' | 'danger'
}

export const useCursor = () => {
  const cursorState = useState<CursorState>('vedanam_cursor', () => ({
    label: '',
    isActive: false,
    variant: 'default'
  }))

  const setCursor = (label: string, variant: 'default' | 'pill' | 'highlight' | 'danger' = 'pill') => {
    cursorState.value = {
      label,
      isActive: true,
      variant
    }
  }

  const resetCursor = () => {
    cursorState.value = {
      label: '',
      isActive: false,
      variant: 'default'
    }
  }

  return {
    cursorState,
    setCursor,
    resetCursor
  }
}
