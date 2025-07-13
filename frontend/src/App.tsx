import { ChatBox } from "@/components/chatbox";

export default function App() {
  return (
    <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-background dark:text-foreground">
      <div className="w-full max-w-4xl h-[60vh] flex items-center justify-center ">
        <ChatBox />
      </div>
    </div>
  );
}
