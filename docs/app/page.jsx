import Link from 'next/link'
// import LiquidEther from '@/components/LiquidEther';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 text-center bg-black text-white">
       
      <h1 className="text-3xl font-mono font-bold mb-4">
        parsec
      </h1>
      <p className="text-2xl mb-8 text-gray-150">
        Structured output generation for LLMs
      </p>
      <Link
        href="/docs"
        className="px-4 py-2 text-lg bg-white text-black rounded-full hover:bg-gray-200 transition-colors cursor-pointer"
      >
        View Documentation
      </Link>
       {/* <LiquidEther
        colors={[ '#5227FF', '#FF9FFC', '#B19EEF' ]}
        mouseForce={20}
        cursorSize={100}
        isViscous={false}

        viscous={30}

        iterationsViscous={32}

        iterationsPoisson={32}

        resolution={0.5}

        isBounce={false}

        autoDemo={true}

        autoSpeed={0.5}

        autoIntensity={2.2}

        takeoverDuration={0.25}

        autoResumeDelay={3000}

        autoRampDuration={0.6}

  /> */}
    </div>
  )
}
