import { describe, expect, it } from 'vitest'
import { flagEmoji, initials } from './display'

describe('initials', () => {
  it.each([
    ['Asha Rao', 'AR'],
    ['Lars de Jong', 'LJ'],
    ['  Yuki  ', 'Y'],
  ])('%s → %s', (name, expected) => {
    expect(initials(name)).toBe(expected)
  })
})

describe('flagEmoji', () => {
  it('turns an ISO country code into its flag', () => {
    expect(flagEmoji('IN')).toBe('🇮🇳')
    expect(flagEmoji('JP')).toBe('🇯🇵')
  })

  it('returns nothing for codes it cannot represent', () => {
    expect(flagEmoji('india')).toBe('')
  })
})
