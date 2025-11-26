import { Footer, Layout, Navbar } from 'nextra-theme-docs'
import { getPageMap } from 'nextra/page-map'
import 'nextra-theme-docs/style.css'

const navbar = (
  <Navbar
    logo={<b>parsec</b>}
    projectLink="https://github.com/olliekm/parsec"
  />
)
const footer = <Footer>MIT {new Date().getFullYear()} © parsec</Footer>

export default async function DocsLayout({ children }) {
  return (
    <Layout
      navbar={navbar}
      pageMap={await getPageMap()}
      docsRepositoryBase="https://github.com/olliekm/parsec/tree/main/docs"
      footer={footer}
    >
      {children}
    </Layout>
  )
}
