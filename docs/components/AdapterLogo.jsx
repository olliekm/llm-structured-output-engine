'use client'

import { useTheme } from 'nextra-theme-docs'
import { useEffect, useState } from 'react'

export default function AdapterLogo({ src }) {
  const { resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const [svgContent, setSvgContent] = useState('')

  useEffect(() => {
    setMounted(true)
    fetch(src)
      .then(res => res.text())
      .then(setSvgContent)
      .catch(console.error)
  }, [src])

  if (!mounted || !svgContent) {
    return <div className="w-12 h-12" />
  }

  const isDark = resolvedTheme === 'dark'

  return (
    <div
      className="w-12 h-12 [&_svg]:w-full [&_svg]:h-full"
      style={{ color: isDark ? 'white' : 'black' }}
      dangerouslySetInnerHTML={{ __html: svgContent }}
    />
  )
}
