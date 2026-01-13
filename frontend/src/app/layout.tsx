import './globals.css'
export const metadata = { title: 'Content Forge', description: 'AI-powered social media campaigns' }
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#0f0f17]">{children}</body>
    </html>
  )
}
