"use client"

import { useState, FormEvent } from "react"
import { Box, Button, TextField, Typography, Alert } from "@mui/material";

import { registerUser } from "@/lib/api/registration"

export default function RegisterPage() {

    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")

    const [emailError, setEmailError] = useState("")
    const [passwordError, setPasswordError] = useState("")
    const [confirmPasswordError, setConfirmPasswordError] = useState("")

    const [isSubmitting, setIsSubmitting] = useState(false)

    const [submitError, setSubmitError] = useState("")
    const [submitSuccess, setSubmitSuccess] = useState(false)

    function validateForm(): boolean {
        let valid = true

        setEmailError("")
        setPasswordError("")
        setConfirmPasswordError("")

        if (!email.trim()) {
            setEmailError("กรุณากรอกอีเมล")
            valid = false
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
            setEmailError("รูปแบบอีเมลไม่ถูกต้อง")
            valid = false
        }

        if (!password) {
            setPasswordError("กรุณากรอกรหัสผ่าน")
            valid = false
        }

        if (!confirmPassword) {
            setConfirmPasswordError("กรุณายืนยันรหัสผ่าน")
            valid = false
        } else if (password !== confirmPassword) {
            setConfirmPasswordError("รหัสผ่านไม่ตรงกัน")
            valid = false
        }
        return valid
    }

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()

        if (isSubmitting || submitSuccess) return;

        if (!validateForm()) return;

        setIsSubmitting(true)
        setSubmitError("")

        try {
            const result = await registerUser(email, password)

            switch (result.status) {
                case "success":
                    setSubmitSuccess(true)
                    setPassword("")
                    setConfirmPassword("")
                    break
                case "conflict":
                    setSubmitError("ไม่สามารถลงทะเบียนได้ กรุณาตรวจสอบข้อมูล")
                    break
                case "validation_error":
                    switch (result.code) {
                        case "INVALID_EMAIL":
                            setEmailError("รูปแบบอีเมลไม่ถูกต้อง")
                            break
                        case "INVALID_PASSWORD_LENGTH":
                            setPasswordError("รหัสผ่านต้องมีความยาว 8 ตัวอักษรขึ้นไป")
                            break
                        case "PASSWORD_REJECTED":
                            setPasswordError("ไม่สามารถใช้รหัสผ่านนี้ได้ กรุณาเลือกรหัสผ่านอื่น")
                            break
                        default:
                            setSubmitError("ข้อมูลลงทะเบียนไม่ถูกต้อง กรุณาตรวจสอบข้อมูล")
                    }
                    break
                case "rate_limited":
                    setSubmitError("มีคำขอมากเกินไป กรุณาลองใหม่ภายหลัง")
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
                p: 2
            }}
        >
            <Box
                component="main"
                sx={{
                    width: "100%",
                    maxWidth: 420,
                    bgcolor: "background.paper",
                    borderRadius: "16px",
                    p: 3,
                    display: "flex",
                    flexDirection: "column",
                    gap: 2
                }}
            >
                <Typography 
                    variant="h5" 
                    variantMapping={{ h5: "h1" }} 
                    sx={{ fontWeight: 600 }}
                >
                    สมัครสมาชิก Kijflow
                </Typography>
                <Box
                    component="form"
                    onSubmit={ handleSubmit }
                    noValidate
                    sx={{
                        display: "flex",
                        flexDirection: "column",
                        gap: 2
                    }}
                >
                    <TextField
                        error={ Boolean(emailError) }
                        helperText={ emailError }
                        value={ email }
                        onChange={ (event) => setEmail(event.target.value) }
                        id="register-email"
                        name="email"
                        label="อีเมล"
                        type="email"
                        autoComplete="email"
                        fullWidth
                        required
                    />
                    <TextField
                        error={ Boolean(passwordError) }
                        helperText={ passwordError ||
                            "รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร และควรเป็นรหัสที่คาดเดายาก"
                         }
                        value={ password }
                        onChange={ (event) => setPassword(event.target.value) }
                        id="register-password"
                        name="password"
                        label="รหัสผ่าน"
                        type="password"
                        autoComplete="new-password"
                        fullWidth
                        required
                    />
                    <TextField
                        error={ Boolean(confirmPasswordError) }
                        helperText={ confirmPasswordError }
                        value={ confirmPassword }
                        onChange={ (event) => setConfirmPassword(event.target.value) }
                        id="register-confirm-password"
                        name="confirmPassword"
                        label="ยืนยันรหัสผ่าน"
                        type="password"
                        autoComplete="new-password"
                        fullWidth
                        required
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
                        sx={{ py: 1.5 }}
                    >
                        สมัครสมาชิก
                    </Button>
                </Box>
            </Box>
        </Box>
    )
}