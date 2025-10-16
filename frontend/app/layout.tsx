import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Phone Usage Dashboard',
  description: 'Visualize your Android app usage statistics',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
