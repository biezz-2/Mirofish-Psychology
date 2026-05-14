import { describe, it, expect } from 'vitest'
import router from '../router/index.js'

describe('router', () => {
  it('includes Integration route', () => {
    const names = router.getRoutes().map((r) => r.name)
    expect(names).toContain('Integration')
  })
})
