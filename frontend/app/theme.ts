"use client";

import { createTheme } from "@mui/material/styles";

export const kijflowTheme = createTheme({
    palette: {
        mode: "light",
        primary: {
            main: "#6D28D9"
        },
        background: {
            default: "#F8F7FC",
            paper: "#FFFFFF"
        }
    },
    shape: {
        borderRadius: 10
    },
    typography: {
        fontFamily: "var(--font-noto-sans-thai), sans-serif"
    },
    components: {
        MuiOutlinedInput: {
            styleOverrides: {
                root: {
                    borderRadius: 10,
                    "& .MuiOutlinedInput-notchedOutline": {
                        borderColor: "#858C99"
                    },
                    "&:hover .MuiOutlinedInput-notchedOutline": {
                        borderColor: "#667085"
                    },
                    "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
                        borderColor: "#6D28D9"
                    }
                }
            }
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    "&.Mui-focusVisible": {
                        outline: "3px solid #6D28D9",
                        outlineOffset: "3px"
                    }
                }
            }
        }
    }
})