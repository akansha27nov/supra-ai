import './globals.css';

export const metadata = {
  title: 'Supra AI - Enterprise Compliance',
  description: 'Enterprise Compliance & Audit Management',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* Google Fonts (Plus Jakarta Sans, Inter, JetBrains Mono) */}
        <link 
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700&family=Inter:wght@400;500;700&family=JetBrains+Mono:wght@500&display=swap" 
          rel="stylesheet" 
        />
        {/* Google Material Symbols */}
        <link 
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" 
          rel="stylesheet" 
        />
      </head>
      <body className="bg-background text-on-background antialiased">
        {children}
      </body>
    </html>
  );
}