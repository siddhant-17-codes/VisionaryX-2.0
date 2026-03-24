import Sidebar from "./Sidebar";

export default function Layout({ children, showSidebar = true }) {
  if (!showSidebar) return <>{children}</>;
  return (
    <div className="flex min-h-screen bg-base">
      <Sidebar />
      <main className="flex-1 overflow-y-auto min-w-0">{children}</main>
    </div>
  );
}
