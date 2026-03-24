import { useNavigate } from "react-router-dom";

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center px-8">
      <div className="text-6xl font-extrabold text-primary mb-4">404</div>
      <h1 className="text-xl font-bold text-linen mb-2">Page not found</h1>
      <p className="text-sm text-muted mb-8">This page doesn't exist in the VisionaryX workspace.</p>
      <button onClick={() => navigate("/")} className="btn-primary">
        Back to home
      </button>
    </div>
  );
}
