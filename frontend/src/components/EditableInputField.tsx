'use client'

import {ChangeEvent, useCallback, useState} from 'react'
import {MdEdit} from 'react-icons/md'
import {FormKey, FormTemplate} from '@/types/Forms'
import Input from './Input'
import RichTextEditor from './RichTextEditor'

interface EditableInputFieldProps {
    fieldName: FormKey
    originalValue: string | string[]
    isEditingForm: boolean
    label: string
    setIsEditingForm: (isEditingForm: boolean) => void
    setFormTemplate: (formTemplate: FormTemplate) => void
    formTemplate: FormTemplate
    type: 'input' | 'textarea'
}

const EditableInputField = ({
    fieldName,
    formTemplate,
    isEditingForm,
    label,
    originalValue,
    setIsEditingForm,
    setFormTemplate,
    type,
}: EditableInputFieldProps) => {
    const [isEditing, setIsEditing] = useState<boolean>(false)

    const handleEditField = () => {
        if (!isEditingForm) {
            setIsEditingForm(true)
        }
        setIsEditing(true)
    }

    const handleInputFieldChange = useCallback(
        (
            event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
            name: FormKey
        ) => {
            setFormTemplate({...formTemplate, [name]: event.target.value})
        },
        [formTemplate, setFormTemplate]
    )

    const handleReset = () => {
        setIsEditing(false)
        setFormTemplate({...formTemplate, [fieldName]: originalValue})
    }

    const getInputElement = useCallback(() => {
        if (type === 'input') {
            return (
                <Input
                    name={fieldName}
                    onChange={handleInputFieldChange}
                    value={formTemplate[fieldName] || ''}
                />
            )
        }
        if (type === 'textarea') {
            return (
                <RichTextEditor
                    name={fieldName}
                    onChange={handleInputFieldChange}
                    value={formTemplate[fieldName] || ''}
                />
            )
        }
        return null
    }, [fieldName, formTemplate, handleInputFieldChange, type])

    return (
        <div className='mb-1 w-full'>
            <div className='flex flex-row items-center gap-2'>
                <label
                    htmlFor={fieldName}
                    className='text-lg font-extrabold capitalize text-slate-800'>
                    {label}
                </label>
                {isEditing ? (
                    <button onClick={handleReset}>reset</button>
                ) : (
                    <MdEdit
                        className='cursor-pointer'
                        onClick={handleEditField}
                    />
                )}
            </div>
            {isEditing ? getInputElement() : <p>{formTemplate[fieldName]}</p>}
        </div>
    )
}

export default EditableInputField
