export type SessionResult =
    | { status: "authenticated" }
    | { status: "unauthenticated" }
    | { status: "uncertain" }

export async function checkSession(): Promise<SessionResult> {
    try {
        const response = await fetch("/auth/session", {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        })

        switch (response.status) {
            case 204:
                return { status: "authenticated" }
            case 401:
                return { status: "unauthenticated" }
            case 503:
                return { status: "uncertain" }
            default:
                return { status: "uncertain" }
        }
    } catch {
        return { status: "uncertain" }
    }
}