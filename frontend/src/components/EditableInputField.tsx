'use client'

import {ChangeEvent, useState} from 'react'
import {MdEdit} from 'react-icons/md'
import {FormKey, FormTemplate} from '@/types/Forms'

interface EditableInputFieldProps {
    fieldName: FormKey
    originalValue: string | string[]
    isEditingForm: boolean
    label: string
    setIsEditingForm: (isEditingForm: boolean) => void
    setFormTemplate: (formTemplate: FormTemplate) => void
    formTemplate: FormTemplate
}

const EditableInputField = ({
    fieldName,
    originalValue,
    isEditingForm,
    setIsEditingForm,
    label,
    setFormTemplate,
    formTemplate,
}: EditableInputFieldProps) => {
    const [isEditing, setIsEditing] = useState<boolean>(false)

    const handleEditField = () => {
        if (!isEditingForm) {
            setIsEditingForm(true)
        }
        setIsEditing(true)
    }

    const handleInputFieldChange = (event: ChangeEvent<HTMLInputElement>) => {
        setFormTemplate({...formTemplate, [fieldName]: event.target.value})
    }

    const handleReset = () => {
        setIsEditing(false)
        setFormTemplate({...formTemplate, [fieldName]: originalValue})
    }

    return (
        <div className='mb-1'>
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
            {isEditing ? (
                <input
                    name={fieldName}
                    className='rounded-md border-2 border-gray-300 px-1 text-slate-500'
                    onChange={handleInputFieldChange}
                    value={formTemplate[fieldName]}
                />
            ) : (
                <p>{formTemplate[fieldName]}</p>
            )}
        </div>
    )
}

export default EditableInputField
