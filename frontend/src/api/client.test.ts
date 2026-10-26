import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, apiFetch, toQueryString } from './client'

function respond(status: number, body?: unknown) {
  vi.stubGlobal(
    'fetch',
    vi
      .fn()
      .mockResolvedValue(
        new Response(body === undefined ? null : JSON.stringify(body), { status }),
      ),
  )
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('apiFetch', () => {
  it('returns parsed JSON on success', async () => {
    respond(200, { ok: true })

    await expect(apiFetch('/health')).resolves.toEqual({ ok: true })
  })

  it('returns undefined for 204 No Content', async () => {
    respond(204)

    await expect(apiFetch('/employees/1', { method: 'DELETE' })).resolves.toBeUndefined()
  })

  it('turns the error envelope into an ApiError with field messages', async () => {
    respond(409, {
      error: {
        code: 'duplicate_employee',
        message: 'An employee with this email already exists',
        fields: { email: 'Already in use' },
      },
    })

    const error = await apiFetch('/employees', { method: 'POST' }).catch((e: unknown) => e)

    expect(error).toBeInstanceOf(ApiError)
    expect(error).toMatchObject({
      status: 409,
      code: 'duplicate_employee',
      fields: { email: 'Already in use' },
    })
  })

  it('still produces an ApiError when the body is not JSON', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('Bad gateway', { status: 502 })))

    await expect(apiFetch('/health')).rejects.toMatchObject({ status: 502, code: 'http_error' })
  })
})

describe('toQueryString', () => {
  it('drops empty values and encodes the rest', () => {
    expect(toQueryString({ q: 'rao & co', country: '', page: 2, department: undefined })).toBe(
      '?q=rao+%26+co&page=2',
    )
  })
})
