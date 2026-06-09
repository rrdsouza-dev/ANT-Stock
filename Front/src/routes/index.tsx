import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "ANT Stock" },
      { name: "description", content: "ANT Stock - Gestão de estoque e logística escolar." },
      { property: "og:title", content: "ANT Stock" },
      { property: "og:description", content: "Gestão de estoque e logística escolar." },
    ],
  }),
  component: Index,
});

function Index() {
  if (typeof window !== "undefined") {
    window.location.replace("/frontend/index.html");
  }
  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "sans-serif" }}>
      <a href="/frontend/index.html">Abrir ANT Stock →</a>
    </div>
  );
}
