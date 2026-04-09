import "./globals.css";

export const metadata = {
  title: "AI Talent Scoring",
  description: "Поиск перспективных GitHub кандидатов"
};

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
