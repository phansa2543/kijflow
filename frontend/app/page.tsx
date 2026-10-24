import { Box, Button, TextField, Typography } from "@mui/material";

export default function Home() {
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
        <Typography variant="h5">
          Kijflow Theme Test
        </Typography>
        <TextField label="ทดสอบช่องกรอกข้อมูล" fullWidth />
        <Button variant="contained">
          ทดสอบปุ่ม
        </Button>
      </Box>
    </Box>
  )
}