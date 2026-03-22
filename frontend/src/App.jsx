import { Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout";
import Home from "./pages/Home";
import Chat from "./pages/Chat";
import PDFChat from "./pages/PDFChat";
import ImageQuery from "./pages/ImageQuery";
import TextToImage from "./pages/TextToImage";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/pdf" element={<PDFChat />} />
        <Route path="/image" element={<ImageQuery />} />
        <Route path="/generate" element={<TextToImage />} />
      </Routes>
    </Layout>
  );
}
