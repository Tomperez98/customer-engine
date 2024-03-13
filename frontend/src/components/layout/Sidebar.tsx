'use client'

import React, {useState} from 'react'
import Link from 'next/link'
import classNames from 'classnames'
import {motion} from 'framer-motion'

const Sidebar = () => {
    const [isExpanded, setIsExpanded] = useState<boolean>(false)
    return (
        <motion.div
            onMouseEnter={() => setIsExpanded(true)}
            onMouseLeave={() => setIsExpanded(false)}
            animate={{
                width: isExpanded ? 288 : 64,
            }}
            className={classNames(
                'flex flex-col items-center justify-center gap-4 border-2 border-r bg-white text-lg  text-neutral-800 shadow-sm',
                isExpanded ? 'w-72 px-4 py-8' : 'w-16 p-8'
            )}>
            <Link href='/dashboard'>
                <div className='font-extrabold'>
                    {isExpanded ? 'Customer Engine' : 'CE'}
                </div>
            </Link>
            <div>
                <Link href='/automatic-responses/create'>
                    <div className='text-md w-full rounded-md px-2 py-1 font-medium hover:bg-orange-400 hover:text-white'>
                        + {isExpanded && 'Crear Formulario'}
                    </div>
                </Link>
            </div>
        </motion.div>
    )
}

export default Sidebar
