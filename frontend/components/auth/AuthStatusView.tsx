"use client"

import type { ReactNode, Ref } from "react"
import { Box, Typography } from "@mui/material"

type AuthStatusViewProps = {
    icon: ReactNode
    title: string
    description: string
    children?: ReactNode
    titleRef?: Ref<HTMLHeadingElement>
}

export default function AuthStatusView({
    icon,
    title,
    description,
    children,
    titleRef
}: AuthStatusViewProps) {
    return (
        <Box
            sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 3,
                minWidth: 0,
                textAlign: "center"
            }}
        >
            <Box aria-hidden="true" sx={{ display: "flex" }}>
                {icon}
            </Box>

            <Box sx={{ width: "100%", overflowWrap: "anywhere" }}>
                <Typography
                    component="h1"
                    variant="h5"
                    ref={titleRef}
                    tabIndex={titleRef ? -1 : undefined}
                    sx={{ fontWeight: 700, lineHeight: 1.5 }}
                >
                    {title}
                </Typography>

                <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mt: 1, lineHeight: 1.75 }}
                >
                    {description}
                </Typography>
            </Box>

            {children && (
                <Box sx={{ width: "100%" }}>
                    {children}
                </Box>
            )}
        </Box>
    )
}