import {FormKey} from '@/types/Forms'
import {ChangeEvent, useEffect, useRef, useState} from 'react'
import ReactHtmlParser from 'react-html-parser'

interface RichTextEditorProps {
    value: string | string[]
    onChange: (
        e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
        name: FormKey
    ) => void
    name: FormKey
    setFormTemplate?: any
    formTemplate?: any
}

type Formats = {
    [key: string]: {
        opening: string
        closing: string
    }
}

const FORMATS: Formats = {
    bold: {
        opening: '<b>',
        closing: '</b>',
    },
    italic: {
        opening: '<i>',
        closing: '</i>',
    },
    strikeTrough: {
        opening: '<s>',
        closing: '</s>',
    },
}

const RichTextEditor = ({
    name,
    onChange,
    value,
    setFormTemplate,
    formTemplate,
}: RichTextEditorProps) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const [selectedText, setSelectedText] = useState<any>({
        selectionStart: '',
        selectionEnd: '',
        selectedText: '',
    })
    const textAsString = value as String

    useEffect(() => {
        const textarea = textareaRef.current
        if (textarea) {
            const handleSelect = () => {
                if (textarea) {
                    const selectionStart = textarea.selectionStart
                    const selectionEnd = textarea.selectionEnd
                    const selectedText = textarea.value.substring(
                        selectionStart,
                        selectionEnd
                    )

                    setSelectedText({
                        selectionStart,
                        selectionEnd,
                        selectedText,
                    })
                }
            }

            textarea.addEventListener('select', handleSelect)

            return () => {
                textarea.removeEventListener('select', handleSelect)
            }
        }
    }, [])

    const handleFormatText = (format: string) => {
        const textBefore = textAsString.substring(
            0,
            selectedText.selectionStart
        )
        const textAfter = textAsString.substring(selectedText.selectionEnd)
        const newText = `${textBefore}${FORMATS[format].opening}${selectedText.selectedText}${FORMATS[format].closing}${textAfter}`

        setFormTemplate((prevState: any) => ({
            ...prevState,
            [name]: newText,
        }))
    }

    return (
        <div className='w-100 flex flex-row'>
            <div className='w-9/12 rounded-md border-2 border-gray-300'>
                {/* <div className='flex gap-2 border-b-2 border-gray-300 bg-gray-200 p-1'>
                    <button onClick={() => handleFormatText('bold')}>
                        bold
                    </button>
                    <button onClick={() => handleFormatText('italic')}>
                        italic
                    </button>
                    <button onClick={() => handleFormatText('strikeTrough')}>
                        crossed
                    </button>
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
