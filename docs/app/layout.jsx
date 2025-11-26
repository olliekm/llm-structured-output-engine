import './globals.css'

export const metadata = {
  title: 'parsec',
  description: 'Structured output generation for LLMs'
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  )
}
