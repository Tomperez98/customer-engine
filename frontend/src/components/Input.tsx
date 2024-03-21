import {InputName} from '@/types/Inputs'
import {ChangeEvent} from 'react'

interface InputProps {
    value: string | string[]
    onChange: (
        e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
        name: InputName
    ) => void
    name: InputName
}

const Input = ({name, onChange, value}: InputProps) => {
    return (
        <input
            name={name}
            className='w-full rounded-md border-2 border-gray-300 px-1 text-slate-500'
            onChange={(e) => onChange(e, name)}
            value={value || ''}
        />
    )
}

export default Input
