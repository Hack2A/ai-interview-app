import { Stack } from "expo-router";

import "../global.css";

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,   // Auth screens usually hide header
        animation: "slide_from_right",
      }}
    />
  );
}
