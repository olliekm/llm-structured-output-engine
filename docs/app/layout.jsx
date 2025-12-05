import './globals.css'

export const metadata = {
  title: 'parsec',
  description: 'Structured output generation for LLMs',
  icons: {
    icon: '/favicon.ico',
  }
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="stylesheet" href="https://use.typekit.net/yqf3hci.css" />
      </head>
      <body className="font-tiempos">{children}</body>
    </html>
  )
}
