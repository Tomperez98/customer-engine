import {useState} from 'react'
import IconButton from '@/components/IconButton'
import {MdCancel, MdCheckCircle} from 'react-icons/md'

interface EditableCellProps {
    initialValue: string
    onCancel: () => void
    onSubmit: (data: string) => void
}

const EditableCell = ({
    initialValue,
    onCancel,
    onSubmit,
}: EditableCellProps) => {
    const [inputValue, setInputValue] = useState<string>(initialValue)
    return (
        <div className='flex-start flex gap-2'>
            <input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                className='rounded-md border-2 border-gray-300 px-1 text-slate-500'
                type='text'
            />
            <IconButton
                Icon={MdCheckCircle}
                onClick={() => onSubmit(inputValue)}
                size='text-lg'
            />
            <IconButton Icon={MdCancel} onClick={onCancel} size='text-lg' />
        </div>
    )
}

export default EditableCell
