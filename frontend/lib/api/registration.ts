export type RegistrationResult = 
    | { status: "success" }
    | {
        status: "validation_error"
        code:
            | "INVALID_EMAIL"
            | "INVALID_PASSWORD_LENGTH"
            | "PASSWORD_REJECTED"
            | "REGISTRATION_FAILED"
    }
    |{
        status: "rate_limited"
        retryAfterSeconds: number | null
    }
    | {
        status: 
            | "conflict"
            | "unavailable"
            | "error"
    }

type RegistrationErrorResponse = {
    error?: {
        code?: unknown
    }
}

function parseRetryAfter(value: string | null): number | null {
    if (value === null) return null

    const trimmed = value.trim()

    if (/^\d+$/.test(trimmed)) {
        const seconds = Number(trimmed)

        return Number.isSafeInteger(seconds) && seconds > 0
            ? seconds : null
    }

    const httpDatePattern = /^(Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{2} (Jan|Feb|Mar|Apr|May|Jun|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} GMT$/

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

export async function registerUser(
    email: string,
    password: string
): Promise<RegistrationResult> {
    try {
        const response = await fetch("/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "same-origin",
            cache: "no-store",
            body: JSON.stringify({
                email,
                password
            })
        })

        switch (response.status) {
            case 201:
                return { status: "success" }
            case 409:
                return { status: "conflict" }
            case 422:
                let code: unknown
                try {
                    const data: RegistrationErrorResponse = 
                        await response.json()
                    code = data?.error?.code
                } catch {
                    return {
                        status: "validation_error",
                        code: "REGISTRATION_FAILED"
                    }
                }
                switch (code) {
                    case "INVALID_EMAIL":
                    case "INVALID_PASSWORD_LENGTH":
                    case "PASSWORD_REJECTED":
                        return {
                            status: "validation_error",
                            code
                        }
                    default:
                        return {
                            status: "validation_error",
                            code: "REGISTRATION_FAILED"
                        }
                }
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
        return { status: "unavailable" }
    }
}