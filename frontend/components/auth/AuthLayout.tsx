"use client"

import type { ReactNode } from "react"
import { Box } from "@mui/material"

type AuthLayoutProps = {
    children: ReactNode
}

export default function AuthLayout({ children }: AuthLayoutProps) {
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
                <Box
                    component="img"
                    src="/kijflow-logo.svg"
                    alt="Kijflow"
                    sx={{
                        display: "block",
                        width: 220,
                        maxWidth: "100%",
                        height: "auto",
                        mx: "auto"
                    }}
                />

                {children}
            </Box>
        </Box>
    )
}