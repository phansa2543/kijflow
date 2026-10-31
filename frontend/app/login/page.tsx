"use client"

import { useState, useEffect, type FormEvent, type ReactNode } from "react"
import { 
    Alert,
    Box,
    Button,
    CircularProgress,
    TextField,
    Typography,
    IconButton,
    InputAdornment
} from "@mui/material"
import { Visibility, VisibilityOff } from "@mui/icons-material"

import { loginUser } from "@/lib/api/login"
import { checkSession } from "@/lib/api/session"

const alertSx = {
    border: 1,
    borderColor: "currentColor",
    alignItems: "flex-start",
    "& .MuiAlert-message": {
        minWidth: 0,
        lineHeight: 1.75,
        overflowWrap: "anywhere"
    }
}

const buttonSx = {
    minHeight: 48,
    py: 1.5,
    fontSize: "1rem",
    fontWeight: 600,
    lineHeight: 1.5,
    textTransform: "none",
    overflowWrap: "anywhere",
    boxShadow: "none",
    "&:hover": { boxShadow: "none" }
}

function LoginCard({ children }: { children: ReactNode }) {
    return (
        <Box
            sx={{
                minHeight: "100dvh",
                boxSizing: "border-box",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                bgcolor: "background.default",
                color: "text.primary",
                px: { xs: 2, sm: 3 },
                py: { xs: 4, sm: 6 }
            }}
        >
            <Box
                component="main"
                aria-labelledby="login-heading"
                sx={{
                    width: "100%",
                    maxWidth: 420,
                    minWidth: 0,
                    boxSizing: "border-box",
                    bgcolor: "background.paper",
                    borderRadius: "16px",
                    border: 1,
                    borderColor: "divider",
                    boxShadow: 2,
                    p: { xs: 3, sm: 4 },
                    display: "flex",
                    flexDirection: "column",
                    gap: 3,
                    overflowWrap: "anywhere"
                }}
            >
                <Typography
                    id="login-heading"
                    variant="h5"
                    component="h1"
                    sx={{ fontWeight: 700, lineHeight: 1.5 }}
                >
                    เข้าสู่ระบบ Kijflow
                </Typography>
                { children }
            </Box>
        </Box>
    )
}

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
    const [showPassword, setShowPassword] = useState(false)

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
            <LoginCard>
                <Box
                    role="status"
                    aria-live="polite"
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        gap: 2,
                        py: 1,
                        textAlign: "center"
                    }}
                >
                    <CircularProgress size={28} aria-hidden="true" />
                    <Typography color="text.secondary" sx={{ lineHeight: 1.75 }}>
                        กำลังตรวจสอบสถานะการเข้าสู่ระบบ...
                    </Typography>
                </Box>
            </LoginCard>
        )
    }

    if (authState === "authenticated") {
        return (
            <LoginCard>
                <Alert
                    severity="success"
                    role="status"
                    sx={ alertSx }
                >
                    เข้าสู่ระบบสำเร็จและยืนยัน Session แล้ว
                </Alert>
                <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ lineHeight: 1.75 }}
                >
                    ยืนยัน Global User Identity แล้ว
                </Typography>
            </LoginCard>
        )
    }

    return (
        <LoginCard>
            <Box
                component="form"
                onSubmit={ handleSubmit }
                noValidate
                aria-busy={ isSubmitting }
                sx={{
                    display: "flex",
                    flexDirection: "column",
                    gap: 2.5,
                    minWidth: 0
                }}
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
                    disabled={ isSubmitting }
                />
                <TextField
                    id="login-password"
                    label="รหัสผ่าน"
                    type={ showPassword ? "text" : "password" }
                    autoComplete="current-password"
                    value={ password }
                    onChange={(event) => setPassword(event.target.value)}
                    fullWidth
                    required
                    disabled={ isSubmitting }
                    slotProps={{
                        input: {
                            endAdornment: (
                                <InputAdornment position="end">
                                    <IconButton
                                        type="button"
                                        edge="end"
                                        aria-label={
                                            showPassword ? "ซ่อนรหัสผ่าน" : "แสดงรหัสผ่าน"
                                        }
                                        aria-pressed={ showPassword }
                                        disabled={ isSubmitting }
                                        onClick={() => setShowPassword((previous) => !previous)}
                                        sx={{
                                            minWidth: 44,
                                            minHeight: 44,
                                            "&Mui-focusVisible": {
                                                outline: "2px solid",
                                                outlineColor: "primary.main",
                                                outlineOffset: 2
                                            }
                                        }}
                                    >
                                        { showPassword ? <VisibilityOff /> : <Visibility /> }
                                    </IconButton>
                                </InputAdornment>
                            )
                        }
                    }}
                />
                {
                    error && (
                        <Alert
                            severity={ authState === "uncertain" ? "warning" : "error" }
                            role="alert"
                            sx={ alertSx }
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
                            loading={ isSubmitting }
                            onClick={ retrySessionCheck }
                            sx={ buttonSx }
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
                    loading={ isSubmitting }
                    sx={ buttonSx }
                >
                    { isSubmitting ? "กำลังเข้าสู่ระบบ..." : "เข้าสู่ระบบ" }
                </Button>
            </Box>
        </LoginCard>
    )
}
