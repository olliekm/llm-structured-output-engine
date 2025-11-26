import { Footer, Layout, Navbar } from 'nextra-theme-docs'
import { Head } from 'nextra/components'
import { getPageMap } from 'nextra/page-map'
import 'nextra-theme-docs/style.css'

export const metadata = {
  title: 'LLM Structured Output Engine',
  description: 'Documentation for LLM Structured Output Engine'
}

const navbar = (
  <Navbar
    logo={<b>LLM Structured Output Engine</b>}
    projectLink="https://github.com/olliekm/llm-structured-output-engine"
  />
)
const footer = <Footer>MIT {new Date().getFullYear()} © LLM Structured Output Engine</Footer>

export default async function RootLayout({ children }) {
  return (
    <html
      lang="en"
      dir="ltr"
      suppressHydrationWarning
    >
      <Head />
      <body>
        <Layout
          navbar={navbar}
          pageMap={await getPageMap()}
          docsRepositoryBase="https://github.com/oliverkwun-morfitt/llm-structured-output-engine/tree/main/docs"
          footer={footer}
        >
          {children}
        </Layout>
      </body>
    </html>
  )
}
