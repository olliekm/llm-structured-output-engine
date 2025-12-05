import Link from 'next/link'
// import Prism from '@/components/Prism';
import PixelBlast from '@/components/PixelBlast'

export default function Home() {
  return (
    <div className="relative min-h-screen bg-white text-black">
      {/* OLD DARK VERSION WITH PRISM BACKGROUND */}
      {/* <div className="absolute inset-0">
        <Prism
          animationType="rotate"
          timeScale={0.5}
          height={3.5}
          baseWidth={5.5}
          scale={2}
          hueShift={0}
          colorFrequency={1}
          noise={0.1}
          glow={1}
        />
      </div>
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen p-8 text-center">
        <h1 className="text-4xl font-bold mb-4">
          parsec
        </h1>
        <p className="text-2xl mb-8 text-gray-150">
          Structured output generation for LLMs
        </p>
        <Link
          href="/docs"
          className="px-8 border-2 border-white hover:bg-transparent py-2 text-lg bg-white text-black rounded-full hover:text-white transition-colors duration-150 ease-in-out cursor-pointer"
        >
          View Documentation
        </Link>
      </div> */}
          {/* NEW LIGHT VERSION - ANTHROPIC INSPIRED */}
      <div className="flex flex-col items-center justify-center min-h-screen px-8 py-16">
        {/* Header */}
        <div className="max-w-4xl w-full text-center mb-16">
          <div className="inline-block px-4 py-1.5 mb-6 text-sm font-medium text-orange-700 bg-orange-50 rounded-full border border-orange-200">
            v0.2.0 - Now with caching and prompt templates
          </div>

          <h1 className="text-6xl sm:text-7xl font-light mb-6 tracking-tight text-gray-900">
            parsec
          </h1>

          <p className="text-xl sm:text-2xl text-gray-600 font-light mb-12 max-w-2xl mx-auto leading-relaxed">
            Structured output generation for LLMs. Predictable, validated, and production-ready.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/docs"
              className="px-8 py-3 text-base font-medium bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200"
            >
              Read Documentation
            </Link>
            <Link
              href="/docs/get-started"
              className="px-8 py-3 text-base font-medium bg-white text-black border border-gray-300 rounded-lg hover:border-gray-400 transition-colors duration-200"
            >
              Get Started
            </Link>
          </div>
        </div>

        {/* Code Example */}
        <div className="max-w-3xl w-full mb-16">
          <div className="bg-gray-50 rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200 bg-white">
              <span className="text-sm font-medium text-gray-600">Quick example</span>
            </div>
            <div className="p-6">
              <pre className="text-sm overflow-x-auto">
                <code className="text-gray-800">
{`from parsec import EnforcementEngine, OpenAIAdapter
from parsec.validators import JSONSchemaValidator

# Define your schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"}
    }
}

# Get structured output
adapter = OpenAIAdapter(api_key="...")
validator = JSONSchemaValidator(schema)
engine = EnforcementEngine(adapter, validator)

result = await engine.enforce(
    "Extract: John is 30 years old",
    schema
)
# {"name": "John", "age": 30}`}
                </code>
              </pre>
            </div>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="max-w-5xl w-full mb-16">
          <h2 className="text-3xl font-light text-center mb-12 text-gray-900">
            Built for production
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-4 bg-blue-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2 text-gray-900">Validated Output</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Automatic validation and repair ensures you always get the structure you expect
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-4 bg-green-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2 text-gray-900">Multi-Provider</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Works with OpenAI, Anthropic, and Gemini. Switch providers without rewriting code
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-4 bg-purple-50 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium mb-2 text-gray-900">Production Ready</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Caching, versioned templates, logging, and comprehensive testing support
              </p>
            </div>
          </div>
        </div>

        {/* Footer CTA */}
        <div className="max-w-2xl w-full text-center">
          <p className="text-gray-600 mb-6">
            Open source and actively maintained
          </p>
          <div className="flex gap-6 justify-center text-sm">
            <a
              href="https://github.com/olliekm/parsec"
              className="text-gray-600 hover:text-gray-900 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            <a
              href="https://github.com/olliekm/parsec/issues"
              className="text-gray-600 hover:text-gray-900 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              Issues
            </a>
            <a
              href="https://pypi.org/project/parsec-llm/"
              className="text-gray-600 hover:text-gray-900 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              PyPI
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
