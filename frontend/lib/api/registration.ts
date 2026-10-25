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
    | {
        status: 
            | "conflict"
            | "rate_limited"
            | "unavailable"
            | "error"
    }

type RegistrationErrorResponse = {
    error?: {
        code?: unknown
    }
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
                return { status: "rate_limited" }
            case 503:
                return { status: "unavailable" }
            default:
                return { status: "error" }
        }
    } catch {
        return { status: "unavailable" }
    }
}