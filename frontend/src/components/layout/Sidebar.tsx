'use client'

import React, {useState} from 'react'
import Link from 'next/link'
import classNames from 'classnames'
import {motion} from 'framer-motion'
import {
    MdOutlineHome,
    MdOutlineAddBox,
    MdOutlineArticle,
    MdOutlineMessage,
} from 'react-icons/md'

const Sidebar = () => {
    const [isExpanded, setIsExpanded] = useState<boolean>(false)
    return (
        <motion.nav
            onMouseEnter={() => setIsExpanded(true)}
            onMouseLeave={() => setIsExpanded(false)}
            animate={{
                width: isExpanded ? 288 : 64,
            }}
            className={classNames(
                'relative flex flex-col items-center justify-center gap-4 border-2 border-r bg-white text-lg  text-neutral-800 shadow-sm',
                isExpanded ? 'w-72 px-4 py-8' : 'w-16 p-8'
            )}>
            <Link className='absolute top-8' href='/dashboard'>
                <div className='font-extrabold'>
                    {isExpanded ? 'Customer Engine' : 'CE'}
                </div>
            </Link>
            <div className='my-8 border-y border-slate-300 py-8'>
                <Link href='/dashboard'>
                    <div className='flex w-full  flex-row items-center gap-1 py-1 text-xl font-medium'>
                        <MdOutlineHome /> {isExpanded && 'Inicio'}
                    </div>
                </Link>
                <Link href='/automatic-responses/create'>
                    <div className='text-md flex  w-full flex-row items-center gap-1 py-1 font-medium'>
                        <MdOutlineAddBox /> {isExpanded && 'Crear Formulario'}
                    </div>
                </Link>
                <Link href='/tokens'>
                    <div className='text-md flex  w-full flex-row items-center gap-1 py-1 font-medium'>
                        <MdOutlineArticle /> {isExpanded && 'Tokens'}
                    </div>
                </Link>
                <Link href='/unmatched-prompts'>
                    <div className='text-md flex  w-full flex-row items-center gap-1 py-1 font-medium'>
                        <MdOutlineMessage />
                        {isExpanded && 'Mensajes sin formulario'}
                    </div>
                </Link>
            </div>
        </motion.nav>
    )
}

export default Sidebar
