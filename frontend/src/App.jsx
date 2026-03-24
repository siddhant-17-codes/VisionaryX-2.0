import { Routes, Route, Navigate } from "react-router-dom";
import { SessionProvider } from "./context/SessionContext";
import Layout from "./components/layout/Layout";
import Landing from "./pages/Landing";
import Chat from "./pages/Chat";
import PDFChat from "./pages/PDFChat";
import ImageQuery from "./pages/ImageQuery";
import TextToImage from "./pages/TextToImage";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <SessionProvider>
      <Routes>
        {/* Landing — no sidebar */}
        <Route path="/" element={<Landing />} />

        {/* Workspace — with sidebar */}
        <Route
          path="/workspace/*"
          element={
            <Layout showSidebar={true}>
              <Routes>
                <Route path="chat"     element={<Chat />} />
                <Route path="pdf"      element={<PDFChat />} />
                <Route path="image"    element={<ImageQuery />} />
                <Route path="generate" element={<TextToImage />} />
                <Route path=""         element={<Navigate to="chat" replace />} />
              </Routes>
            </Layout>
          }
        />

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </SessionProvider>
  );
}
