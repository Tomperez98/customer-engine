'use client'

import {useState} from 'react'
import {MdEdit} from 'react-icons/md'

interface EditableInputFieldProps {
    fieldName: string
    originalValue: string | string[]
    isEditingForm: boolean
    label: string
    setIsEditingForm: (isEditingForm: boolean) => void
    setEditedForm: any
    editedForm: any
}

const EditableInputField = ({
    fieldName,
    originalValue,
    isEditingForm,
    setIsEditingForm,
    label,
    setEditedForm,
    editedForm,
}: EditableInputFieldProps) => {
    const [isEditing, setIsEditing] = useState<boolean>(false)

    const handleEditField = () => {
        if (!isEditingForm) {
            setIsEditingForm(true)
        }
        setIsEditing(true)
    }

    const handleInputFieldChange = (event: any) => {
        setEditedForm({...editedForm, [fieldName]: event.target.value})
    }

    const handleReset = () => {
        setIsEditing(false)
        setEditedForm({...editedForm, [fieldName]: originalValue})
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
                    value={editedForm[fieldName]}
                />
            ) : (
                <p>{editedForm[fieldName]}</p>
            )}
        </div>
    )
}

export default EditableInputField
