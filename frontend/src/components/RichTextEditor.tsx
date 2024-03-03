import {FormKey} from '@/types/Forms'
import {ChangeEvent} from 'react'

interface RichTextEditorProps {
    value: string | string[]
    onChange: (
        e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
        name: FormKey
    ) => void
    name: FormKey
}

const RichTextEditor = ({name, onChange, value}: RichTextEditorProps) => {
    return (
        <textarea
            className='w-full rounded-md border-2 border-gray-300 px-1 text-slate-500'
            name={name}
            onChange={(e) => onChange(e, name)}
            rows={10}
            value={value || ''}
        />
    )
}

export default RichTextEditor
