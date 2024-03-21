import classNames from 'classnames'
import {motion} from 'framer-motion'
import React from 'react'

interface ButtonProps {
    label: string
    onClick: () => void
    disabled?: boolean
    style?: 'secondary'
    className?: string
    size?: 'sm' | 'xl'
}

const Button = ({
    className,
    disabled,
    label,
    onClick,
    size,
    style,
}: ButtonProps) => {
    const animationProps = disabled
        ? {}
        : {
              whileHover: {scale: 1.1},
              whileTap: {scale: 0.9},
          }
    return (
        <motion.button
            className={classNames(
                className,
                'box-border cursor-pointer rounded-full',
                {
                    'border border-neutral-800 bg-neutral-800 text-white hover:border-transparent hover:bg-cyan-400 disabled:cursor-default  disabled:border-slate-200 disabled:bg-slate-200':
                        !style,
                    'border border-gray-400 bg-transparent text-gray-400 disabled:cursor-default disabled:border-slate-200 disabled:text-slate-200':
                        style === 'secondary',
                    'px-5 py-1.5 text-sm': !size,
                    'px-4 py-1 text-xs': size === 'sm',
                    'px-16 py-4 text-xl': size === 'xl',
                }
            )}
            disabled={disabled}
            onClick={onClick}
            {...animationProps}>
            {label}
        </motion.button>
    )
}

export default Button
