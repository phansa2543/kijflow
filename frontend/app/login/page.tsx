"use client"

import { useState, useEffect, type FormEvent } from "react"
import { 
    Alert,
    Box,
    Button,
    TextField,
    Typography
} from "@mui/material"

import { loginUser } from "@/lib/api/login"
import { checkSession } from "@/lib/api/session"

export default function LoginPage() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [error, setError] = useState("")

    type AuthState =
    | "checking"
    | "unauthenticated"
    | "authenticated"
    | "uncertain"

    const [authState, setAuthState] = useState<AuthState>("checking")

    useEffect(() => {
        let cancelled = false

        async function verifyInitialSession() {
            const session = await checkSession()

            if (cancelled) return

            switch (session.status) {
                case "authenticated":
                    setAuthState("authenticated")
                    setPassword("")
                    break

                case "unauthenticated":
                    setAuthState("unauthenticated")
                    break

                case "uncertain":
                    setAuthState("uncertain")
                    setError("ไม่สามารถตรวจสอบสถานะการเข้าสู่ระบบได้ กรุณาลองอีกครั้ง")
                    break
            }
        }

        void verifyInitialSession()

        return () => {
            cancelled = true
        }
    }, [])

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        if (isSubmitting) return

        setError("")

        if (!email.trim() || !password) {
            setError("กรุณากรอกอีเมลและรหัสผ่าน")
            return
        }

        setAuthState("checking")
        setIsSubmitting(true)

        try {
            const login = await loginUser(email, password)

            switch (login.status) {
                case "success":
                    const session = await checkSession()

                    if (session.status === "authenticated") {
                        setAuthState("authenticated")
                        setPassword("")
                        return
                    }

                    if (session.status === "unauthenticated") {
                        setAuthState("unauthenticated")
                        setError("ไม่สามารถยืนยันการเข้าสู่ระบบได้ กรุณาลองอีกครั้ง")
                        return
                    }
                    setAuthState("uncertain")
                    setError("ไม่สามารถตรวจสอบสถานะได้ กรุณาลองตรวจสอบอีกครั้ง")
                    return
                case "invalid_credentials":
                    setAuthState("unauthenticated")
                    setError("อีเมลหรือรหัสผ่านไม่ถูกต้อง")
                    return
                case "rate_limited":
                    setAuthState("unauthenticated")
                    setError(
                        login.retryAfterSeconds !== null
                            ? `มีการเข้าสู่ระบบหลายครั้งเกินไป กรุณาลองใหม่ใน ${login.retryAfterSeconds} วินาที`
                            : "มีการเข้าสู่ระบบหลายครั้งเกินไป กรุณาลองใหม่ภายหลัง"
                    )
                    return
                case "unavailable":
                case "uncertain":
                    setAuthState("uncertain")
                    setError("ไม่สามารถยืนยันผลการเข้าสู่ระบบได้ กรุณาตรวจสอบสถานะอีกครั้ง")
                    return
                default:
                    setAuthState("uncertain")
                    setError("ไม่สามารถยืนยันผลการเข้าสู่ระบบได้ กรุณาตรวจสอบสถานะอีกครั้ง")
                    return
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    async function retrySessionCheck() {
        if (isSubmitting) return

        setIsSubmitting(true)
        setError("")

        try {
            const session = await checkSession()

            switch (session.status) {
                case "authenticated":
                    setAuthState("authenticated")
                    setPassword("")
                    break
                case "unauthenticated":
                    setAuthState("unauthenticated")
                    setError("กรุณาเข้าสู่ระบบอีกครั้ง")
                    break
                case "uncertain":
                    setAuthState("uncertain")
                    setError("ยังไม่สามารถตรวจสอบสถานะได้ กรุณาลองอีกครั้ง")
                    break
            }
        } finally {
            setIsSubmitting(false)
        }
    }

    if (authState === "checking") {
        return (
            <Box
                component="main"
                sx={{
                    minHeight: "100vh",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center"
                }}
            >
                <Typography role="status">
                    กำลังตรวจสอบสถานะการเข้าสู่ระบบ...
                </Typography>
            </Box>
        )
    }

    if (authState === "authenticated") {
        return (
            <Box
                component="main"
                sx={{ p: 4 }}
            >
                <Alert
                    severity="success"
                >
                    เข้าสู่ระบบสำเร็จและยืนยัน Session แล้ว
                </Alert>
                <Typography
                    sx={{ mt: 2 }}
                >
                    ยืนยัน Global User Identity แล้ว
                </Typography>
            </Box>
        )
    }

    return (
        <Box
            sx={{
                minHeight: "100vh",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                p: 2
            }}
        >
            <Box
                sx={{
                    width: "100%",
                    maxWidth: 420
                }}
            >
                <Typography
                    variant="h4"
                    component="h1"
                    gutterBottom
                >
                    เข้าสู่ระบบ Kijflow
                </Typography>
                <Box
                    component="form"
                    onSubmit={ handleSubmit }
                    noValidate
                >
                    <TextField
                        id="login-email"
                        label="อีเมล"
                        type="email"
                        autoComplete="username"
                        value={ email }
                        onChange={(event) => setEmail(event.target.value)}
                        fullWidth
                        required
                        margin="normal"
                        disabled={ isSubmitting }
                    />
                    <TextField
                        id="login-password"
                        label="รหัสผ่าน"
                        type="password"
                        autoComplete="current-password"
                        value={ password }
                        onChange={(event) => setPassword(event.target.value)}
                        fullWidth
                        required
                        margin="normal"
                        disabled={ isSubmitting }
                    />
                    {
                        error && (
                            <Alert
                                severity="error"
                                role="alert"
                                sx={{ mt: 2 }}
                            >
                                { error }
                            </Alert>
                        )
                    }
                    {
                        authState === "uncertain" && !isSubmitting && (
                            <Button
                                type="button"
                                variant="outlined"
                                fullWidth
                                disabled={ isSubmitting }
                                onClick={ retrySessionCheck }
                                sx={{ mt: 2 }}
                            >
                                ตรวจสอบสถานะอีกครั้ง
                            </Button>
                        )
                    }
                    <Button
                        type="submit"
                        variant="contained"
                        fullWidth
                        disabled={ isSubmitting }
                        sx={{ mt: 3 }}
                    >
                        { isSubmitting ? "กำลังเข้าสู่ระบบ..." : "เข้าสู่ระบบ" }
                    </Button>
                </Box>
            </Box>
        </Box>
    )
}