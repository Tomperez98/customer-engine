import classNames from 'classnames'
import React from 'react'

interface ButtonProps {
    label: string
    onClick: () => void
    disabled?: boolean
    style?: 'secondary'
}

const Button = ({disabled, label, onClick, style}: ButtonProps) => {
    return (
        <button
            className={classNames(
                'cursor-pointer rounded-full px-6 py-1.5 text-white',
                {
                    'bg-neutral-900 disabled:cursor-default disabled:bg-slate-200':
                        !style,
                    'border-2 border-gray-400 bg-transparent text-gray-400':
                        style === 'secondary',
                }
            )}
            disabled={disabled}
            onClick={onClick}>
            {label}
        </button>
    )
}

export default Button
