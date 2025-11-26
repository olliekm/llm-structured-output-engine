import Link from 'next/link'
import Prism from '@/components/Prism';

export default function Home() {
  return (
    <div className="relative min-h-screen bg-black text-white">
      <div className="absolute inset-0">
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
      </div>
    </div>
  )
}
