export type LoginResult = 
    | { status: "success" }
    | { status: "invalid_credentials" }
    | { status: "rate_limited"; retryAfterSeconds: number | null }
    | { status: "unavailable" }
    | { status: "uncertain" }
    | { status: "error" }

function parseRetryAfter(value: string | null): number | null {
    if (value === null) return null

    const trimmed = value.trim()

    if (/^\d+$/.test(trimmed)) {
        const seconds = Number(trimmed)

        return Number.isSafeInteger(seconds) && seconds > 0
            ? seconds : null
    }

    const httpDatePattern = /^(Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} GMT$/

    if (!httpDatePattern.test(trimmed)) return null

    const date = Date.parse(trimmed)

    if (
        !Number.isFinite(date) ||
        new Date(date).toUTCString() !== trimmed
    ) {
        return null
    }

    const seconds = Math.ceil((date - Date.now()) / 1000)

    return Number.isSafeInteger(seconds) && seconds > 0
        ? seconds : null
}

export async function loginUser(
    email: string,
    password: string
): Promise<LoginResult> {
    try {
        const response = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "same-origin",
            cache: "no-store",
            body: JSON.stringify({ email, password })
        })

        switch (response.status) {
            case 200:
                return { status: "success" }
            case 401:
                return { status: "invalid_credentials" }
            case 429:
                return {
                    status: "rate_limited",
                    retryAfterSeconds: parseRetryAfter(
                        response.headers.get("Retry-After")
                    )
                }
            case 503:
                return { status: "unavailable" }
            default:
                return { status: "error" }
        }
    } catch {
        return { status: "uncertain" }
    }
}