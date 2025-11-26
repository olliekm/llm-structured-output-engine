import React from 'react'
import ParsecLogo from '../parsec_logo.svg'
import Image from 'next/image'

type Props = {}

function Logo({}: Props) {
  return (
    <div className='flex'>
        <Image
          src={ParsecLogo}
          alt="Parsec Logo"
          width={40}
          height={50}
        />
        <span className=' font-bold text-xl self-center'>parsec</span>
    </div>
  )
}

export default Logo