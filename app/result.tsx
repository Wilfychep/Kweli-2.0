// app/result.tsx
import ResultScreen from "../screens/ResultScreen";
import { Stack } from "expo-router";

export default function ResultPage() {
    return (
        <>
            <Stack.Screen
                options={{
                    title: "Analysis Result",
                    headerShown: false, // Since you have your own header in ResultScreen
                }}
            />
            <ResultScreen />
        </>
    );
}