"use client"

import { Visibility, VisibilityOff } from "@mui/icons-material"

import { useState, useRef, useEffect, FormEvent } from "react"
import { 
    Box, 
    Button, 
    TextField, 
    Typography, 
    Alert,
    IconButton,
    InputAdornment
} from "@mui/material";

import { registerUser } from "@/lib/api/registration"

export default function RegisterPage() {

    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")

    const [emailError, setEmailError] = useState("")
    const [passwordError, setPasswordError] = useState("")

    const [isSubmitting, setIsSubmitting] = useState(false)

    const [submitError, setSubmitError] = useState("")
    const [submitSuccess, setSubmitSuccess] = useState(false)

    const [showPassword, setShowPassword] = useState(false)

    const emailInputRef = useRef<HTMLInputElement>(null)
    const passwordInputRef = useRef<HTMLInputElement>(null)

    type FocusTarget = "email" | "password"
    const [focusRequest, setFocusRequest] = useState<{
        target: FocusTarget
        sequence: number
    } | null>(null)

    function requestFieldFocus(target: FocusTarget) {
        setFocusRequest((previous) => ({
            target,
            sequence: (previous?.sequence ?? 0) + 1
        }))
    }

    useEffect(() => {
        if (!focusRequest) return

        if (focusRequest.target === "email") {
            emailInputRef.current?.focus()
        } else {
            passwordInputRef.current?.focus()
        }
    }, [focusRequest])

    function validateForm(): boolean {
        let valid = true
        let isEmailInvalid = false

        setEmailError("")
        setPasswordError("")

        if (!email.trim()) {
            setEmailError("กรุณากรอกอีเมล")
            valid = false
            isEmailInvalid = true
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
            setEmailError("รูปแบบอีเมลไม่ถูกต้อง")
            valid = false
            isEmailInvalid = true
        }

        if (!password) {
            setPasswordError("กรุณากรอกรหัสผ่าน")
            valid = false
        }

        if (!valid) {
            requestFieldFocus(
                isEmailInvalid ? "email" : "password"
            )
        }

        return valid
    }

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        if (isSubmitting || submitSuccess) return;

        setSubmitError("")

        if (!validateForm()) return;

        setIsSubmitting(true)   

        try {
            const result = await registerUser(email, password)

            switch (result.status) {
                case "success":
                    setSubmitSuccess(true)
                    setPassword("")
                    break
                case "conflict":
                    setSubmitError("ไม่สามารถลงทะเบียนได้ กรุณาตรวจสอบข้อมูล")
                    break
                case "validation_error":
                    switch (result.code) {
                        case "INVALID_EMAIL":
                            setEmailError("รูปแบบอีเมลไม่ถูกต้อง")
                            requestFieldFocus("email")
                            break
                        case "INVALID_PASSWORD_LENGTH":
                            setPasswordError("รหัสผ่านต้องมีความยาว 8 ตัวอักษรขึ้นไป")
                            requestFieldFocus("password")
                            break
                        case "PASSWORD_REJECTED":
                            setPasswordError("ไม่สามารถใช้รหัสผ่านนี้ได้ กรุณาเลือกรหัสผ่านอื่น")
                            requestFieldFocus("password")
                            break
                        default:
                            setSubmitError("ข้อมูลลงทะเบียนไม่ถูกต้อง กรุณาตรวจสอบข้อมูล")
                    }
                    break
                case "rate_limited":
                    if (result.retryAfterSeconds !== null) {
                        setSubmitError(`มีคำขอมากเกินไป กรุณารอประมาณ ${result.retryAfterSeconds} วินาทีก่อนลองใหม่`)
                    } else {
                        setSubmitError("มีคำขอมากเกินไป กรุณาลองใหม่ภายหลัง")
                    }
                    break
                case "unavailable":
                    setSubmitError("ไม่สามารถยืนยันผลการลงทะเบียนได้ในขณะนี้ กรุณาลองตรวจสอบอีกครั้งภายหลัง")
                    break
                default:
                    setSubmitError("เกิดข้อผิดพลาด กรุณาลองใหม่ภายหลัง")
            }
        } finally {
            setIsSubmitting(false)
        }
    }

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
                sx={{
                    width: "100%",
                    maxWidth: 420,
                    boxSizing: "border-box",
                    bgcolor: "background.paper",
                    borderRadius: "16px",
                    border: 1,
                    borderColor: "divider",
                    boxShadow: 2,
                    p: { xs: 3, sm: 4 },
                    display: "flex",
                    flexDirection: "column",
                    gap: 3
                }}
            >
                <Box component="header">
                    <Typography
                        variant="h5"
                        variantMapping={{ h5: "h1" }}
                        sx={{ fontWeight: 700, lineHeight: 1.5 }}
                    >
                        สมัครสมาชิก Kijflow
                    </Typography>
                    <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mt: 1, lineHeight: 1.75 }}
                    >
                        เริ่มต้นใช้งานด้วยอีเมลและรหัสผ่านของคุณ
                    </Typography>
                </Box>
                <Box
                    component="form"
                    onSubmit={ handleSubmit }
                    noValidate
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        gap: 2.5,
                        minWidth: 0,
                        "& .MuiFormHelperText-root": {
                            mx: 0,
                            mt: 1,
                            lineHeight: 1.75,
                            overflowWrap: "anywhere"
                        },
                        "& .MuiAlert-root": {
                            border: 1,
                            borderColor: "currentColor",
                            alignItems: "flex-start",
                            "& .MuiAlert-message": {
                                minWidth: 0,
                                lineHeight: 1.75,
                                overflowWrap: "anywhere"
                            }
                        }
                    }}
                >
                    <TextField
                        inputRef={ emailInputRef }
                        error={ Boolean(emailError) }
                        helperText={ emailError }
                        slotProps={{
                            htmlInput: {
                                "aria-describedby": emailError
                                    ? "register-email-error"
                                    : undefined
                            },
                            formHelperText: {
                                id: "register-email-error"
                            }
                        }}
                        value={ email }
                        onChange={ 
                            (event) => {
                                setEmail(event.target.value)
                                setEmailError("")
                            } 
                        }
                        id="register-email"
                        name="email"
                        label="อีเมล"
                        type="email"
                        autoComplete="email"
                        fullWidth
                        required
                    />
                    <TextField
                        inputRef={ passwordInputRef }
                        error={ Boolean(passwordError) }
                        helperText={ passwordError ||
                            "รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร และควรเป็นรหัสที่คาดเดายาก"
                         }
                        value={ password }
                        onChange={ 
                            (event) => {
                                setPassword(event.target.value)
                                setPasswordError("")
                            } 
                        }
                        id="register-password"
                        name="password"
                        label="รหัสผ่าน"
                        type={ showPassword ? "text" : "password" }
                        autoComplete="new-password"
                        fullWidth
                        required
                        slotProps={{
                            htmlInput: {
                                "aria-describedby": "register-password-helper"
                            },
                            formHelperText: {
                                id: "register-password-helper"
                            },
                            input: {
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton
                                            type="button"
                                            aria-label={
                                                showPassword
                                                    ? "ซ่อนรหัสผ่าน"
                                                    : "แสดงรหัสผ่าน"
                                            }
                                            aria-pressed={ showPassword }
                                            onClick={() => setShowPassword((value) => !value)}
                                            edge="end"
                                            sx={{
                                                minWidth: 44,
                                                minHeight: 44,
                                                "&.Mui-focusVisible": {
                                                    outline: "3px solid",
                                                    outlineColor: "primary.main",
                                                    outlineOffset: "2px"
                                                }
                                            }}
                                        >
                                            { showPassword ? <Visibility /> : <VisibilityOff /> }
                                        </IconButton>
                                    </InputAdornment>
                                )
                            }
                        }}
                    />
                    { submitError && (
                        <Alert severity="error" role="alert">
                            { submitError }
                        </Alert>
                    ) }
                    { submitSuccess && (
                        <Alert severity="success" role="alert">
                            สมัครสมาชิกสำเร็จ
                        </Alert>
                    ) }
                    <Button
                        variant="contained"
                        type="submit"
                        fullWidth
                        disabled={ isSubmitting || submitSuccess }
                        loading={ isSubmitting }
                        sx={{
                            minHeight: 48,
                            py: 1.5,
                            fontSize: "1rem",
                            fontWeight: 600,
                            lineHeight: 1.5,
                            boxShadow: "none",
                            "&:hover": { boxShadow: "none" }
                        }}
                    >
                        สมัครสมาชิก
                    </Button>
                </Box>
            </Box>
        </Box>
    )
}
