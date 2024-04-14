'use client'

import {useRef, useState} from 'react'
import {FaChevronDown, FaChevronUp} from 'react-icons/fa6'
import {motion} from 'framer-motion'
import {useOutsideClick} from '@/hooks/useOutsideClick'

export type DropdownOption = {
    label: string
    value: string
}

interface DropdownProps {
    options: DropdownOption[]
    onSelect: (selectedOption: string) => void
    placeholderText?: string
}

const Dropdown = ({options, onSelect, placeholderText}: DropdownProps) => {
    const containerRef = useRef(null)
    const [isOpen, setIsOpen] = useState<boolean>(false)
    const [selectedLabel, setSelectedLabel] = useState<string>(
        placeholderText || 'Selecciona una opción'
    )

    const handleSelectOption = (option: DropdownOption) => {
        if (selectedLabel === option.label) return

        onSelect(option.value)
        setSelectedLabel(option.label)
        setIsOpen(false)
    }

    useOutsideClick(containerRef, () => setIsOpen(false))
    return (
        <div ref={containerRef} className='relative text-xs text-neutral-800'>
            <button
                className='flex w-48 items-center justify-between rounded-md border-2 border-gray-300 bg-white px-2 py-1.5'
                onClick={() => setIsOpen((prevState) => !prevState)}>
                {selectedLabel}
                {isOpen ? (
                    <FaChevronUp className='ml-3 text-cyan-400' />
                ) : (
                    <FaChevronDown className='ml-3 text-cyan-400' />
                )}
            </button>
            {isOpen && (
                <motion.div
                    initial={{opacity: 0}}
                    animate={{opacity: 1}}
                    exit={{opacity: 0}}
                    className='absolute left-0 top-10 w-full rounded-md bg-white py-2 shadow-md'>
                    <ul>
                        {options.map((option) => {
                            return (
                                <li
                                    className='cursor-pointer select-none px-2 py-1 hover:bg-cyan-400 hover:text-white'
                                    key={option.value}
                                    onClick={() => handleSelectOption(option)}>
                                    {option.label}
                                </li>
                            )
                        })}
                    </ul>
                </motion.div>
            )}
        </div>
    )
}

export default Dropdown
