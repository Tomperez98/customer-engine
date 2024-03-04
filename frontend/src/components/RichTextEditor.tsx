import {FormKey} from '@/types/Forms'
import {ChangeEvent, useEffect, useRef} from 'react'
import ReactHtmlParser from 'react-html-parser'

interface RichTextEditorProps {
    value: string | string[]
    onChange: (
        e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
        name: FormKey
    ) => void
    name: FormKey
}

const RichTextEditor = ({name, onChange, value}: RichTextEditorProps) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null)

    useEffect(() => {
        const textarea = textareaRef.current
        if (textarea) {
            const handleSelect = () => {
                if (textarea) {
                    const start = textarea.selectionStart
                    const end = textarea.selectionEnd

                    const selectedText = textarea.value.substring(start, end)

                    console.log(selectedText)
                }
            }

            textarea.addEventListener('select', handleSelect)

            return () => {
                textarea.removeEventListener('select', handleSelect)
            }
        }
    }, [])

    return (
        <div className='w-100 flex flex-row'>
            <div className='w-9/12 rounded-md border-2 border-gray-300'>
                {/* <div className='border-b-2 border-gray-300 bg-gray-200 p-1'>
                    <button>bold</button>
                </div> */}
                <textarea
                    className='w-full text-slate-500 focus:border-transparent focus:ring-transparent'
                    name={name}
                    onChange={(e) => onChange(e, name)}
                    ref={textareaRef}
                    rows={10}
                    value={value || ''}
                />
            </div>
            {/* <div>{ReactHtmlParser(value as string)}</div> */}
        </div>
    )
}

export default RichTextEditor
